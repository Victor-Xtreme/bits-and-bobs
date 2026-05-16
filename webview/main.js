// Acquire VS Code API (will be mocked in standalone tests)
let vscode;
try {
    vscode = acquireVsCodeApi();
} catch (e) {
    // Running in standalone mode, vscode will be set by test file
    console.log('Running in standalone test mode');
}

// State management
let currentPanel = 'health';
let analysisData = null;
let currentFilter = 'all';
let currentDocsTab = 'docs';
let graphRendered = false; // Track if architecture graph has been rendered

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    showLoadingState();
});

// Message listener from extension
window.addEventListener('message', event => {
    const msg = event.data;
    console.log('Received message:', msg.type);
    
    switch (msg.type) {
        case 'loading':
            showLoadingState(msg.step);
            break;
        case 'progress':
            updateProgress(msg.data);
            break;
        case 'results':
            analysisData = msg.data;
            showResults(msg.data);
            break;
        case 'error':
            showError(msg.message);
            break;
    }
});

// Initialize event listeners
function initializeEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const panel = button.dataset.panel;
            switchPanel(panel);
        });
    });
    
    // Retry button
    const retryButton = document.getElementById('retryButton');
    if (retryButton) {
        retryButton.addEventListener('click', () => {
            vscode.postMessage({ type: 'retry' });
            showLoadingState();
        });
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-button').forEach(button => {
        button.addEventListener('click', () => {
            currentFilter = button.dataset.filter;
            document.querySelectorAll('.filter-button').forEach(b => b.classList.remove('active'));
            button.classList.add('active');
            if (analysisData) {
                renderReviewPanel(analysisData.review);
            }
        });
    });
    
    // Docs tabs
    document.querySelectorAll('.docs-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            currentDocsTab = tab.dataset.tab;
            document.querySelectorAll('.docs-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.getElementById('docsContent').classList.toggle('hidden', currentDocsTab !== 'docs');
            document.getElementById('testsContent').classList.toggle('hidden', currentDocsTab !== 'tests');
        });
    });
    
    // Graph controls
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const resetZoom = document.getElementById('resetZoom');
    const depthSlider = document.getElementById('depthSlider');
    const depthValue = document.getElementById('depthValue');
    const networkView = document.getElementById('networkView');
    const treeView = document.getElementById('treeView');
    
    if (zoomIn) zoomIn.addEventListener('click', () => zoomGraph(1.2));
    if (zoomOut) zoomOut.addEventListener('click', () => zoomGraph(0.8));
    if (resetZoom) resetZoom.addEventListener('click', () => resetGraphZoom());
    
    if (depthSlider && depthValue) {
        depthSlider.addEventListener('input', (e) => {
            const newDepth = parseInt(e.target.value);
            depthValue.textContent = newDepth;
            currentDepth = newDepth;
            if (currentArchitecture && currentSelectedNode && currentGraphView === 'tree') {
                renderDependencyTree(currentSelectedNode, currentDepth);
            }
        });
    }
    
    // View toggle buttons
    if (networkView) {
        networkView.addEventListener('click', () => {
            currentGraphView = 'network';
            networkView.classList.add('active');
            treeView.classList.remove('active');
            document.getElementById('depthControl').style.display = 'none';
            if (currentArchitecture) {
                renderNetworkGraph(currentArchitecture);
            }
        });
    }
    
    if (treeView) {
        treeView.addEventListener('click', () => {
            currentGraphView = 'tree';
            treeView.classList.add('active');
            networkView.classList.remove('active');
            document.getElementById('depthControl').style.display = 'flex';
            if (currentArchitecture && currentSelectedNode) {
                renderDependencyTree(currentSelectedNode, currentDepth);
            }
        });
    }
}

// Show loading state
function showLoadingState(step = 'Initializing...') {
    hideAllStates();
    const loadingState = document.getElementById('loadingState');
    loadingState.classList.remove('hidden');
    
    const loadingStep = document.getElementById('loadingStep');
    if (loadingStep) {
        loadingStep.textContent = step;
    }
}

// Update progress
function updateProgress(data) {
    const progressFill = document.getElementById('progressFill');
    if (progressFill && data.percentage !== undefined) {
        progressFill.style.width = `${data.percentage}%`;
    }
    
    if (data.step) {
        const loadingStep = document.getElementById('loadingStep');
        if (loadingStep) {
            loadingStep.textContent = data.step;
        }
    }
}

// Show error state
function showError(message) {
    hideAllStates();
    const errorState = document.getElementById('errorState');
    errorState.classList.remove('hidden');
    
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
    }
}

// Show results
function showResults(data) {
    hideAllStates();
    
    // Store data for lazy rendering
    analysisData = data;
    
    // Render panels that are immediately visible
    renderHealthPanel(data.health);
    // Architecture panel will be rendered lazily when user switches to it
    renderReviewPanel(data.review);
    renderDocsPanel(data.documentation);
    renderSecurityPanel(data.security);
    
    // Update badges
    updateBadges(data);
    
    // Show the health panel by default
    switchPanel('health');
}

// Hide all state panels
function hideAllStates() {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
}

// Switch between panels
function switchPanel(panelName) {
    currentPanel = panelName;
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.toggle('active', button.dataset.panel === panelName);
    });
    
    // Update panels
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.add('hidden');
    });
    
    const targetPanel = document.getElementById(`${panelName}Panel`);
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
        
        // Lazy render architecture graph when panel becomes visible
        if (panelName === 'architecture' && analysisData && !graphRendered) {
            // Small delay to ensure panel is fully visible and has dimensions
            setTimeout(() => {
                renderArchitecturePanel(analysisData.architecture);
                graphRendered = true;
            }, 50);
        }
    }
}

// Update badge counts
function updateBadges(data) {
    const reviewBadge = document.getElementById('reviewBadge');
    const securityBadge = document.getElementById('securityBadge');
    
    if (reviewBadge && data.review && data.review.findings) {
        const count = data.review.findings.length;
        reviewBadge.textContent = count > 0 ? count : '';
        reviewBadge.style.display = count > 0 ? 'inline-block' : 'none';
    }
    
    if (securityBadge && data.security && data.security.issues) {
        const count = data.security.issues.length;
        securityBadge.textContent = count > 0 ? count : '';
        securityBadge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

// Render Health Panel
function renderHealthPanel(health) {
    if (!health) return;
    
    const scoreNum = document.getElementById('scoreNum');
    const ringFill = document.getElementById('ringFill');
    const gradeBadge = document.getElementById('gradeBadge');
    const summary = document.getElementById('summary');
    const priorityList = document.getElementById('priorityList');
    
    // Animate score
    animateScore(0, health.score, 1000, scoreNum);
    
    // Update ring
    const circumference = 251;
    const offset = circumference - (circumference * health.score) / 100;
    setTimeout(() => {
        ringFill.style.strokeDashoffset = offset;
        
        // Color based on score
        if (health.score >= 90) ringFill.style.stroke = 'var(--rs-green)';
        else if (health.score >= 70) ringFill.style.stroke = 'var(--rs-blue)';
        else if (health.score >= 50) ringFill.style.stroke = 'var(--rs-amber)';
        else ringFill.style.stroke = 'var(--rs-red)';
    }, 100);
    
    // Update grade badge
    gradeBadge.textContent = health.grade;
    gradeBadge.className = 'grade-badge grade-' + health.grade.toLowerCase();
    
    // Update summary
    summary.textContent = health.summary;
    
    // Update priorities
    priorityList.innerHTML = '';
    if (health.priorities && health.priorities.length > 0) {
        health.priorities.forEach(priority => {
            const li = document.createElement('li');
            li.textContent = priority;
            priorityList.appendChild(li);
        });
    }
}

// Animate score number
function animateScore(start, end, duration, element) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(start + (end - start) * easeOutQuart);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Render Architecture Panel - Support both Network and Tree views
let currentArchitecture = null;
let currentSelectedNode = null;
let currentDepth = 1;
let currentGraphView = 'tree'; // 'network' or 'tree'
let graphSimulation = null;

function renderArchitecturePanel(architecture) {
    try {
        // Validation
        if (!architecture || !architecture.nodes || !architecture.edges) {
            console.warn('Architecture data missing or invalid');
            return;
        }
        
        if (typeof d3 === 'undefined') {
            console.error('D3.js library not loaded');
            return;
        }
        
        const container = document.getElementById('graphContainer');
        if (!container) {
            console.error('Graph container not found');
            return;
        }
        
        // Store architecture data
        currentArchitecture = architecture;
        
        // Select first entry node or first node as default
        if (!currentSelectedNode) {
            const entryNode = architecture.nodes.find(n => n.type === 'entry');
            currentSelectedNode = entryNode ? entryNode.id : architecture.nodes[0].id;
        }
        
        // Render based on current view
        if (currentGraphView === 'network') {
            renderNetworkGraph(architecture);
        } else {
            renderDependencyTree(currentSelectedNode, currentDepth);
        }
        
    } catch (error) {
        console.error('Error rendering architecture graph:', error);
        const container = document.getElementById('graphContainer');
        if (container) {
            container.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--vscode-errorForeground);">
                    <div style="text-align: center;">
                        <p style="font-size: 18px; margin-bottom: 8px;">⚠️ Failed to render architecture graph</p>
                        <p style="font-size: 14px; color: var(--vscode-descriptionForeground);">${error.message}</p>
                    </div>
                </div>
            `;
        }
    }
}

// Render Network Graph (Original force-directed layout)
function renderNetworkGraph(architecture) {
    const container = document.getElementById('graphContainer');
    container.innerHTML = '';
    
    const width = container.clientWidth || 1000;
    const height = container.clientHeight || 600;
    
    // Create SVG
    const svg = d3.select('#graphContainer')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g');
    
    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Store zoom for controls
    container._zoom = zoom;
    container._svg = svg;
    
    // Color mapping
    const colorMap = {
        entry: '#3b82f6',
        service: '#8b5cf6',
        util: '#10b981',
        config: '#f59e0b',
        test: '#6b7280'
    };
    
    // Create force simulation
    graphSimulation = d3.forceSimulation(architecture.nodes)
        .force('link', d3.forceLink(architecture.edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));
    
    // Create links
    const link = g.append('g')
        .selectAll('line')
        .data(architecture.edges)
        .join('line')
        .attr('stroke', '#6b7280')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', 2);
    
    // Create nodes
    const node = g.append('g')
        .selectAll('circle')
        .data(architecture.nodes)
        .join('circle')
        .attr('r', 12)
        .attr('fill', d => colorMap[d.type] || '#6b7280')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));
    
    // Add labels
    const label = g.append('g')
        .selectAll('text')
        .data(architecture.nodes)
        .join('text')
        .text(d => d.label || d.name)
        .attr('font-size', 10)
        .attr('dx', 15)
        .attr('dy', 4)
        .attr('fill', '#ffffff');
    
    // Tooltip
    const tooltip = document.getElementById('nodeTooltip');
    
    node.on('mouseover', (event, d) => {
        tooltip.innerHTML = `
            <strong>${d.label || d.name}</strong><br>
            <small>Type: ${d.type}</small><br>
            ${d.description ? `<p style="margin-top: 8px; font-size: 12px;">${d.description}</p>` : ''}
        `;
        tooltip.classList.remove('hidden');
    })
    .on('mousemove', (event) => {
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY + 10) + 'px';
    })
    .on('mouseout', () => {
        tooltip.classList.add('hidden');
    });
    
    // Update positions on tick
    graphSimulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    // Drag functions
    function dragStarted(event, d) {
        if (!event.active) graphSimulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragEnded(event, d) {
        if (!event.active) graphSimulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Build subgraph for selected node
function buildSubgraph(nodeId, allNodes, allEdges, depth) {
    const visited = new Set([nodeId]);
    const dependents = [];
    const dependencies = [];
    const queue = [[nodeId, 0]];
    
    while (queue.length > 0) {
        const [current, d] = queue.shift();
        if (d >= depth) continue;
        
        // Find dependents (nodes that depend on current)
        for (const edge of allEdges) {
            if (edge.target === current && !visited.has(edge.source)) {
                visited.add(edge.source);
                const node = allNodes.find(n => n.id === edge.source);
                if (node) {
                    dependents.push(node);
                    queue.push([edge.source, d + 1]);
                }
            }
        }
        
        // Find dependencies (nodes that current depends on)
        for (const edge of allEdges) {
            if (edge.source === current && !visited.has(edge.target)) {
                visited.add(edge.target);
                const node = allNodes.find(n => n.id === edge.target);
                if (node) {
                    dependencies.push(node);
                    queue.push([edge.target, d + 1]);
                }
            }
        }
    }
    
    // Filter edges to only include those between visible nodes
    const visibleEdges = allEdges.filter(e =>
        visited.has(e.source) && visited.has(e.target)
    );
    
    return {
        selected_node: allNodes.find(n => n.id === nodeId),
        dependents,
        dependencies,
        edges: visibleEdges,
        depth
    };
}

// Render the dependency tree
function renderDependencyTree(nodeId, depth) {
    const container = document.getElementById('graphContainer');
    container.innerHTML = '';
    
    const width = container.clientWidth || 1000;
    const height = container.clientHeight || 600;
    
    // Build subgraph
    const subgraph = buildSubgraph(
        nodeId,
        currentArchitecture.nodes,
        currentArchitecture.edges,
        depth
    );
    
    if (!subgraph.selected_node) {
        console.error('Selected node not found:', nodeId);
        return;
    }
    
    // Create SVG
    const svg = d3.select('#graphContainer')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g');
    
    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Store zoom for controls
    container._zoom = zoom;
    container._svg = svg;
    
    // Color mapping based on NodeType
    const colorMap = {
        entry: '#ef4444',      // coral/red
        service: '#3b82f6',    // blue
        util: '#14b8a6',       // teal
        config: '#f59e0b',     // amber
        test: '#6b7280'        // gray
    };
    
    // Edge relationship line styles
    const edgeStyleMap = {
        imports: { dasharray: 'none', opacity: 0.8 },
        extends: { dasharray: '5,5', opacity: 0.7 },
        calls: { dasharray: '2,3', opacity: 0.6 }
    };
    
    // Layout configuration
    const nodeRadius = 20;
    const verticalSpacing = 100;
    const horizontalSpacing = 150;
    
    // Position nodes
    const allVisibleNodes = [
        ...subgraph.dependents,
        subgraph.selected_node,
        ...subgraph.dependencies
    ];
    
    // Calculate positions
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Position selected node at center
    subgraph.selected_node.x = centerX;
    subgraph.selected_node.y = centerY;
    
    // Position dependents above (in rows)
    const dependentsPerRow = Math.ceil(Math.sqrt(subgraph.dependents.length));
    subgraph.dependents.forEach((node, i) => {
        const row = Math.floor(i / dependentsPerRow);
        const col = i % dependentsPerRow;
        const rowWidth = Math.min(dependentsPerRow, subgraph.dependents.length - row * dependentsPerRow);
        const offsetX = (col - (rowWidth - 1) / 2) * horizontalSpacing;
        
        node.x = centerX + offsetX;
        node.y = centerY - verticalSpacing * (row + 1);
    });
    
    // Position dependencies below (in rows)
    const dependenciesPerRow = Math.ceil(Math.sqrt(subgraph.dependencies.length));
    subgraph.dependencies.forEach((node, i) => {
        const row = Math.floor(i / dependenciesPerRow);
        const col = i % dependenciesPerRow;
        const rowWidth = Math.min(dependenciesPerRow, subgraph.dependencies.length - row * dependenciesPerRow);
        const offsetX = (col - (rowWidth - 1) / 2) * horizontalSpacing;
        
        node.x = centerX + offsetX;
        node.y = centerY + verticalSpacing * (row + 1);
    });
    
    // Create arrow markers for edges
    svg.append('defs').selectAll('marker')
        .data(['arrow'])
        .join('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#6b7280');
    
    // Create edges
    const link = g.append('g')
        .selectAll('line')
        .data(subgraph.edges)
        .join('line')
        .attr('x1', d => {
            const source = allVisibleNodes.find(n => n.id === d.source);
            return source ? source.x : 0;
        })
        .attr('y1', d => {
            const source = allVisibleNodes.find(n => n.id === d.source);
            return source ? source.y : 0;
        })
        .attr('x2', d => {
            const target = allVisibleNodes.find(n => n.id === d.target);
            return target ? target.x : 0;
        })
        .attr('y2', d => {
            const target = allVisibleNodes.find(n => n.id === d.target);
            return target ? target.y : 0;
        })
        .attr('stroke', '#6b7280')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', d => {
            const style = edgeStyleMap[d.relationship] || edgeStyleMap.imports;
            return style.opacity;
        })
        .attr('stroke-dasharray', d => {
            const style = edgeStyleMap[d.relationship] || edgeStyleMap.imports;
            return style.dasharray;
        })
        .attr('marker-end', 'url(#arrow)');
    
    // Create nodes
    const node = g.append('g')
        .selectAll('g')
        .data(allVisibleNodes)
        .join('g')
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .style('cursor', 'pointer')
        .on('click', (event, d) => {
            // Re-root tree at clicked node
            currentSelectedNode = d.id;
            renderDependencyTree(d.id, currentDepth);
        });
    
    // Add circles to nodes
    node.append('circle')
        .attr('r', d => d.id === nodeId ? nodeRadius * 1.2 : nodeRadius)
        .attr('fill', d => colorMap[d.type] || '#6b7280')
        .attr('stroke', d => d.id === nodeId ? '#fff' : 'none')
        .attr('stroke-width', d => d.id === nodeId ? 3 : 0);
    
    // Add labels
    node.append('text')
        .text(d => d.label || d.name)
        .attr('font-size', 11)
        .attr('dy', nodeRadius + 15)
        .attr('text-anchor', 'middle')
        .attr('fill', '#ffffff')
        .style('pointer-events', 'none');
    
    // Tooltip
    const tooltip = document.getElementById('nodeTooltip');
    
    node.on('mouseover', (event, d) => {
        tooltip.innerHTML = `
            <strong>${d.label || d.name}</strong><br>
            <small>Type: ${d.type}</small><br>
            ${d.description ? `<p style="margin-top: 8px; font-size: 12px;">${d.description}</p>` : ''}
        `;
        tooltip.classList.remove('hidden');
    })
    .on('mousemove', (event) => {
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY + 10) + 'px';
    })
    .on('mouseout', () => {
        tooltip.classList.add('hidden');
    });
}

// Graph zoom controls
function zoomGraph(factor) {
    const container = document.getElementById('graphContainer');
    if (container._svg && container._zoom) {
        container._svg.transition().call(
            container._zoom.scaleBy,
            factor
        );
    }
}

function resetGraphZoom() {
    const container = document.getElementById('graphContainer');
    if (container._svg && container._zoom) {
        container._svg.transition().call(
            container._zoom.transform,
            d3.zoomIdentity
        );
    }
}

// Render Review Panel
function renderReviewPanel(review) {
    if (!review || !review.findings) return;
    
    const findingsList = document.getElementById('findingsList');
    const emptyReview = document.getElementById('emptyReview');
    
    // Filter findings
    let filteredFindings = review.findings;
    if (currentFilter === 'high') {
        filteredFindings = review.findings.filter(f => 
            f.severity === 'HIGH' || f.severity === 'CRITICAL'
        );
    } else if (currentFilter === 'critical') {
        filteredFindings = review.findings.filter(f => f.severity === 'CRITICAL');
    }
    
    if (filteredFindings.length === 0) {
        findingsList.innerHTML = '';
        emptyReview.classList.remove('hidden');
        return;
    }
    
    emptyReview.classList.add('hidden');
    
    // Sort by severity
    const severityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
    filteredFindings.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
    
    findingsList.innerHTML = '';
    filteredFindings.forEach(finding => {
        const item = document.createElement('div');
        item.className = `finding-item ${finding.severity.toLowerCase()}`;
        
        item.innerHTML = `
            <div class="finding-header">
                <span class="severity-badge ${finding.severity.toLowerCase()}">${finding.severity}</span>
                <span class="finding-location">${finding.file}:${finding.line}</span>
            </div>
            <div class="finding-description">${finding.message}</div>
            <div class="finding-details">
                <strong>Suggestion:</strong>
                <p>${finding.suggestion || 'No suggestion available'}</p>
            </div>
        `;
        
        item.addEventListener('click', () => {
            item.classList.toggle('expanded');
        });
        
        findingsList.appendChild(item);
    });
}

// Render Docs Panel
function renderDocsPanel(documentation) {
    if (!documentation) return;
    
    const docsContent = document.getElementById('docsContent');
    const testsContent = document.getElementById('testsContent');
    
    // Render documentation
    if (documentation.functions && documentation.functions.length > 0) {
        docsContent.innerHTML = '';
        documentation.functions.forEach(func => {
            const item = document.createElement('div');
            item.className = 'doc-item';
            
            item.innerHTML = `
                <h4>${func.name}</h4>
                <p>${func.description}</p>
                ${func.params ? `<p><strong>Parameters:</strong> ${func.params}</p>` : ''}
                ${func.returns ? `<p><strong>Returns:</strong> ${func.returns}</p>` : ''}
                ${func.example ? `<pre><code>${escapeHtml(func.example)}</code></pre>` : ''}
            `;
            
            docsContent.appendChild(item);
        });
    }
    
    // Render test stubs
    if (documentation.tests && documentation.tests.length > 0) {
        testsContent.innerHTML = '';
        documentation.tests.forEach(test => {
            const item = document.createElement('div');
            item.className = 'doc-item';
            
            item.innerHTML = `
                <h4>${test.name}</h4>
                <pre><code>${escapeHtml(test.code)}</code><button class="copy-button" onclick="copyToClipboard(this)">Copy</button></pre>
            `;
            
            testsContent.appendChild(item);
        });
    }
}

// Render Security Panel
function renderSecurityPanel(security) {
    if (!security) return;
    
    const securityIssues = document.getElementById('securityIssues');
    const emptySecurityIssues = document.getElementById('emptySecurityIssues');
    const modernizationList = document.getElementById('modernizationList');
    
    // Render security issues
    if (security.issues && security.issues.length > 0) {
        emptySecurityIssues.classList.add('hidden');
        securityIssues.innerHTML = '';
        
        security.issues.forEach((issue, index) => {
            const item = document.createElement('div');
            item.className = 'security-item';
            if (index === 0) item.classList.add('fix-first');
            
            item.innerHTML = `
                <div class="security-item-header">
                    ${index === 0 ? '<span style="color: var(--rs-red); font-weight: 600;">⚠️ Fix This First</span>' : ''}
                    <span class="effort-badge ${issue.effort.toLowerCase()}">${issue.effort}</span>
                </div>
                <p><strong>${issue.title}</strong></p>
                <p style="margin-top: 8px; color: var(--vscode-descriptionForeground);">${issue.description}</p>
            `;
            
            securityIssues.appendChild(item);
        });
    } else {
        emptySecurityIssues.classList.remove('hidden');
        securityIssues.innerHTML = '';
    }
    
    // Render modernization
    if (security.modernization && security.modernization.length > 0) {
        modernizationList.innerHTML = '';
        
        security.modernization.forEach(item => {
            const div = document.createElement('div');
            div.className = 'security-item';
            
            div.innerHTML = `
                <div class="security-item-header">
                    <span class="effort-badge ${item.effort.toLowerCase()}">${item.effort}</span>
                </div>
                <p><strong>${item.title}</strong></p>
                <p style="margin-top: 8px; color: var(--vscode-descriptionForeground);">${item.description}</p>
            `;
            
            modernizationList.appendChild(div);
        });
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyToClipboard(button) {
    const code = button.previousElementSibling.textContent;
    navigator.clipboard.writeText(code).then(() => {
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = 'Copy';
        }, 2000);
    });
}

// Export for inline handlers
window.copyToClipboard = copyToClipboard;

// Made with Bob
