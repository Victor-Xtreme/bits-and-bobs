**User:**

<task>
How do I install the extension in 'vscode-extension' (see below for file content)
</task>

<file_content path="vscode-extension">
├── .gitignore
├── .vscode/
├── media/
├── out/
├── package-lock.json
├── package.json
├── README.md
├── SETUP.md
├── src/
├── tsconfig.json
└── webview/

<file_content path="vscode-extension/.gitignore">
1 | node_modules/
2 | .vscode/

</file_content>

<file_content path="vscode-extension/package-lock.json">
   1 | {
   2 |   "name": "reposense",
   3 |   "version": "0.0.1",
   4 |   "lockfileVersion": 3,
   5 |   "requires": true,
   6 |   "packages": {
   7 |     "": {
   8 |       "name": "reposense",
   9 |       "version": "0.0.1",
  10 |       "dependencies": {
  11 |         "node-fetch": "^2.7.0"
  12 |       },
  13 |       "devDependencies": {
  14 |         "@types/node": "16.x",
  15 |         "@types/node-fetch": "^2.6.2",
  16 |         "@types/vscode": "^1.74.0",
  17 |         "@typescript-eslint/eslint-plugin": "^5.45.0",
  18 |         "@typescript-eslint/parser": "^5.45.0",
  19 |         "eslint": "^8.28.0",
  20 |         "typescript": "^4.9.3"
  21 |       },
  22 |       "engines": {
  23 |         "vscode": "^1.74.0"
  24 |       }
  25 |     },
  26 |     "node_modules/@eslint-community/eslint-utils": {
  27 |       "version": "4.9.1",
  28 |       "resolved": "https://registry.npmjs.org/@eslint-community/eslint-utils/-/eslint-utils-4.9.1.tgz",
  29 |       "integrity": "sha512-phrYmNiYppR7znFEdqgfWHXR6NCkZEK7hwWDHZUjit/2/U0r6XvkDl0SYnoM51Hq7FhCGdLDT6zxCCOY1hexsQ==",
  30 |       "dev": true,
  31 |       "license": "MIT",
  32 |       "dependencies": {
  33 |         "eslint-visitor-keys": "^3.4.3"
  34 |       },
  35 |       "engines": {
  36 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
  37 |       },
  38 |       "funding": {
  39 |         "url": "https://opencollective.com/eslint"
  40 |       },
  41 |       "peerDependencies": {
  42 |         "eslint": "^6.0.0 || ^7.0.0 || >=8.0.0"
  43 |       }
  44 |     },
  45 |     "node_modules/@eslint-community/regexpp": {
  46 |       "version": "4.12.2",
  47 |       "resolved": "https://registry.npmjs.org/@eslint-community/regexpp/-/regexpp-4.12.2.tgz",
  48 |       "integrity": "sha512-EriSTlt5OC9/7SXkRSCAhfSxxoSUgBm33OH+IkwbdpgoqsSsUg7y3uh+IICI/Qg4BBWr3U2i39RpmycbxMq4ew==",
  49 |       "dev": true,
  50 |       "license": "MIT",
  51 |       "engines": {
  52 |         "node": "^12.0.0 || ^14.0.0 || >=16.0.0"
  53 |       }
  54 |     },
  55 |     "node_modules/@eslint/eslintrc": {
  56 |       "version": "2.1.4",
  57 |       "resolved": "https://registry.npmjs.org/@eslint/eslintrc/-/eslintrc-2.1.4.tgz",
  58 |       "integrity": "sha512-269Z39MS6wVJtsoUl10L60WdkhJVdPG24Q4eZTH3nnF6lpvSShEK3wQjDX9JRWAUPvPh7COouPpU9IrqaZFvtQ==",
  59 |       "dev": true,
  60 |       "license": "MIT",
  61 |       "dependencies": {
  62 |         "ajv": "^6.12.4",
  63 |         "debug": "^4.3.2",
  64 |         "espree": "^9.6.0",
  65 |         "globals": "^13.19.0",
  66 |         "ignore": "^5.2.0",
  67 |         "import-fresh": "^3.2.1",
  68 |         "js-yaml": "^4.1.0",
  69 |         "minimatch": "^3.1.2",
  70 |         "strip-json-comments": "^3.1.1"
  71 |       },
  72 |       "engines": {
  73 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
  74 |       },
  75 |       "funding": {
  76 |         "url": "https://opencollective.com/eslint"
  77 |       }
  78 |     },
  79 |     "node_modules/@eslint/js": {
  80 |       "version": "8.57.1",
  81 |       "resolved": "https://registry.npmjs.org/@eslint/js/-/js-8.57.1.tgz",
  82 |       "integrity": "sha512-d9zaMRSTIKDLhctzH12MtXvJKSSUhaHcjV+2Z+GK+EEY7XKpP5yR4x+N3TAcHTcu963nIr+TMcCb4DBCYX1z6Q==",
  83 |       "dev": true,
  84 |       "license": "MIT",
  85 |       "engines": {
  86 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
  87 |       }
  88 |     },
  89 |     "node_modules/@humanwhocodes/config-array": {
  90 |       "version": "0.13.0",
  91 |       "resolved": "https://registry.npmjs.org/@humanwhocodes/config-array/-/config-array-0.13.0.tgz",
  92 |       "integrity": "sha512-DZLEEqFWQFiyK6h5YIeynKx7JlvCYWL0cImfSRXZ9l4Sg2efkFGTuFf6vzXjK1cq6IYkU+Eg/JizXw+TD2vRNw==",
  93 |       "deprecated": "Use @eslint/config-array instead",
  94 |       "dev": true,
  95 |       "license": "Apache-2.0",
  96 |       "dependencies": {
  97 |         "@humanwhocodes/object-schema": "^2.0.3",
  98 |         "debug": "^4.3.1",
  99 |         "minimatch": "^3.0.5"
 100 |       },
 101 |       "engines": {
 102 |         "node": ">=10.10.0"
 103 |       }
 104 |     },
 105 |     "node_modules/@humanwhocodes/module-importer": {
 106 |       "version": "1.0.1",
 107 |       "resolved": "https://registry.npmjs.org/@humanwhocodes/module-importer/-/module-importer-1.0.1.tgz",
 108 |       "integrity": "sha512-bxveV4V8v5Yb4ncFTT3rPSgZBOpCkjfK0y4oVVVJwIuDVBRMDXrPyXRL988i5ap9m9bnyEEjWfm5WkBmtffLfA==",
 109 |       "dev": true,
 110 |       "license": "Apache-2.0",
 111 |       "engines": {
 112 |         "node": ">=12.22"
 113 |       },
 114 |       "funding": {
 115 |         "type": "github",
 116 |         "url": "https://github.com/sponsors/nzakas"
 117 |       }
 118 |     },
 119 |     "node_modules/@humanwhocodes/object-schema": {
 120 |       "version": "2.0.3",
 121 |       "resolved": "https://registry.npmjs.org/@humanwhocodes/object-schema/-/object-schema-2.0.3.tgz",
 122 |       "integrity": "sha512-93zYdMES/c1D69yZiKDBj0V24vqNzB/koF26KPaagAfd3P/4gUlh3Dys5ogAK+Exi9QyzlD8x/08Zt7wIKcDcA==",
 123 |       "deprecated": "Use @eslint/object-schema instead",
 124 |       "dev": true,
 125 |       "license": "BSD-3-Clause"
 126 |     },
 127 |     "node_modules/@nodelib/fs.scandir": {
 128 |       "version": "2.1.5",
 129 |       "resolved": "https://registry.npmjs.org/@nodelib/fs.scandir/-/fs.scandir-2.1.5.tgz",
 130 |       "integrity": "sha512-vq24Bq3ym5HEQm2NKCr3yXDwjc7vTsEThRDnkp2DK9p1uqLR+DHurm/NOTo0KG7HYHU7eppKZj3MyqYuMBf62g==",
 131 |       "dev": true,
 132 |       "license": "MIT",
 133 |       "dependencies": {
 134 |         "@nodelib/fs.stat": "2.0.5",
 135 |         "run-parallel": "^1.1.9"
 136 |       },
 137 |       "engines": {
 138 |         "node": ">= 8"
 139 |       }
 140 |     },
 141 |     "node_modules/@nodelib/fs.stat": {
 142 |       "version": "2.0.5",
 143 |       "resolved": "https://registry.npmjs.org/@nodelib/fs.stat/-/fs.stat-2.0.5.tgz",
 144 |       "integrity": "sha512-RkhPPp2zrqDAQA/2jNhnztcPAlv64XdhIp7a7454A5ovI7Bukxgt7MX7udwAu3zg1DcpPU0rz3VV1SeaqvY4+A==",
 145 |       "dev": true,
 146 |       "license": "MIT",
 147 |       "engines": {
 148 |         "node": ">= 8"
 149 |       }
 150 |     },
 151 |     "node_modules/@nodelib/fs.walk": {
 152 |       "version": "1.2.8",
 153 |       "resolved": "https://registry.npmjs.org/@nodelib/fs.walk/-/fs.walk-1.2.8.tgz",
 154 |       "integrity": "sha512-oGB+UxlgWcgQkgwo8GcEGwemoTFt3FIO9ababBmaGwXIoBKZ+GTy0pP185beGg7Llih/NSHSV2XAs1lnznocSg==",
 155 |       "dev": true,
 156 |       "license": "MIT",
 157 |       "dependencies": {
 158 |         "@nodelib/fs.scandir": "2.1.5",
 159 |         "fastq": "^1.6.0"
 160 |       },
 161 |       "engines": {
 162 |         "node": ">= 8"
 163 |       }
 164 |     },
 165 |     "node_modules/@types/json-schema": {
 166 |       "version": "7.0.15",
 167 |       "resolved": "https://registry.npmjs.org/@types/json-schema/-/json-schema-7.0.15.tgz",
 168 |       "integrity": "sha512-5+fP8P8MFNC+AyZCDxrB2pkZFPGzqQWUzpSeuuVLvm8VMcorNYavBqoFcxK8bQz4Qsbn4oUEEem4wDLfcysGHA==",
 169 |       "dev": true,
 170 |       "license": "MIT"
 171 |     },
 172 |     "node_modules/@types/node": {
 173 |       "version": "16.18.126",
 174 |       "resolved": "https://registry.npmjs.org/@types/node/-/node-16.18.126.tgz",
 175 |       "integrity": "sha512-OTcgaiwfGFBKacvfwuHzzn1KLxH/er8mluiy8/uM3sGXHaRe73RrSIj01jow9t4kJEW633Ov+cOexXeiApTyAw==",
 176 |       "dev": true,
 177 |       "license": "MIT"
 178 |     },
 179 |     "node_modules/@types/node-fetch": {
 180 |       "version": "2.6.13",
 181 |       "resolved": "https://registry.npmjs.org/@types/node-fetch/-/node-fetch-2.6.13.tgz",
 182 |       "integrity": "sha512-QGpRVpzSaUs30JBSGPjOg4Uveu384erbHBoT1zeONvyCfwQxIkUshLAOqN/k9EjGviPRmWTTe6aH2qySWKTVSw==",
 183 |       "dev": true,
 184 |       "license": "MIT",
 185 |       "dependencies": {
 186 |         "@types/node": "*",
 187 |         "form-data": "^4.0.4"
 188 |       }
 189 |     },
 190 |     "node_modules/@types/semver": {
 191 |       "version": "7.7.1",
 192 |       "resolved": "https://registry.npmjs.org/@types/semver/-/semver-7.7.1.tgz",
 193 |       "integrity": "sha512-FmgJfu+MOcQ370SD0ev7EI8TlCAfKYU+B4m5T3yXc1CiRN94g/SZPtsCkk506aUDtlMnFZvasDwHHUcZUEaYuA==",
 194 |       "dev": true,
 195 |       "license": "MIT"
 196 |     },
 197 |     "node_modules/@types/vscode": {
 198 |       "version": "1.120.0",
 199 |       "resolved": "https://registry.npmjs.org/@types/vscode/-/vscode-1.120.0.tgz",
 200 |       "integrity": "sha512-feaT4Rst+FkTch5zz/ZbNCxoIvo55YU80Be2kiL7OJcod4+CUYf2lUBPdIJzozNnSEMq1VRTGrWEcCGFB3fBmA==",
 201 |       "dev": true,
 202 |       "license": "MIT"
 203 |     },
 204 |     "node_modules/@typescript-eslint/eslint-plugin": {
 205 |       "version": "5.62.0",
 206 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/eslint-plugin/-/eslint-plugin-5.62.0.tgz",
 207 |       "integrity": "sha512-TiZzBSJja/LbhNPvk6yc0JrX9XqhQ0hdh6M2svYfsHGejaKFIAGd9MQ+ERIMzLGlN/kZoYIgdxFV0PuljTKXag==",
 208 |       "dev": true,
 209 |       "license": "MIT",
 210 |       "dependencies": {
 211 |         "@eslint-community/regexpp": "^4.4.0",
 212 |         "@typescript-eslint/scope-manager": "5.62.0",
 213 |         "@typescript-eslint/type-utils": "5.62.0",
 214 |         "@typescript-eslint/utils": "5.62.0",
 215 |         "debug": "^4.3.4",
 216 |         "graphemer": "^1.4.0",
 217 |         "ignore": "^5.2.0",
 218 |         "natural-compare-lite": "^1.4.0",
 219 |         "semver": "^7.3.7",
 220 |         "tsutils": "^3.21.0"
 221 |       },
 222 |       "engines": {
 223 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 224 |       },
 225 |       "funding": {
 226 |         "type": "opencollective",
 227 |         "url": "https://opencollective.com/typescript-eslint"
 228 |       },
 229 |       "peerDependencies": {
 230 |         "@typescript-eslint/parser": "^5.0.0",
 231 |         "eslint": "^6.0.0 || ^7.0.0 || ^8.0.0"
 232 |       },
 233 |       "peerDependenciesMeta": {
 234 |         "typescript": {
 235 |           "optional": true
 236 |         }
 237 |       }
 238 |     },
 239 |     "node_modules/@typescript-eslint/parser": {
 240 |       "version": "5.62.0",
 241 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/parser/-/parser-5.62.0.tgz",
 242 |       "integrity": "sha512-VlJEV0fOQ7BExOsHYAGrgbEiZoi8D+Bl2+f6V2RrXerRSylnp+ZBHmPvaIa8cz0Ajx7WO7Z5RqfgYg7ED1nRhA==",
 243 |       "dev": true,
 244 |       "license": "BSD-2-Clause",
 245 |       "dependencies": {
 246 |         "@typescript-eslint/scope-manager": "5.62.0",
 247 |         "@typescript-eslint/types": "5.62.0",
 248 |         "@typescript-eslint/typescript-estree": "5.62.0",
 249 |         "debug": "^4.3.4"
 250 |       },
 251 |       "engines": {
 252 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 253 |       },
 254 |       "funding": {
 255 |         "type": "opencollective",
 256 |         "url": "https://opencollective.com/typescript-eslint"
 257 |       },
 258 |       "peerDependencies": {
 259 |         "eslint": "^6.0.0 || ^7.0.0 || ^8.0.0"
 260 |       },
 261 |       "peerDependenciesMeta": {
 262 |         "typescript": {
 263 |           "optional": true
 264 |         }
 265 |       }
 266 |     },
 267 |     "node_modules/@typescript-eslint/scope-manager": {
 268 |       "version": "5.62.0",
 269 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/scope-manager/-/scope-manager-5.62.0.tgz",
 270 |       "integrity": "sha512-VXuvVvZeQCQb5Zgf4HAxc04q5j+WrNAtNh9OwCsCgpKqESMTu3tF/jhZ3xG6T4NZwWl65Bg8KuS2uEvhSfLl0w==",
 271 |       "dev": true,
 272 |       "license": "MIT",
 273 |       "dependencies": {
 274 |         "@typescript-eslint/types": "5.62.0",
 275 |         "@typescript-eslint/visitor-keys": "5.62.0"
 276 |       },
 277 |       "engines": {
 278 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 279 |       },
 280 |       "funding": {
 281 |         "type": "opencollective",
 282 |         "url": "https://opencollective.com/typescript-eslint"
 283 |       }
 284 |     },
 285 |     "node_modules/@typescript-eslint/type-utils": {
 286 |       "version": "5.62.0",
 287 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/type-utils/-/type-utils-5.62.0.tgz",
 288 |       "integrity": "sha512-xsSQreu+VnfbqQpW5vnCJdq1Z3Q0U31qiWmRhr98ONQmcp/yhiPJFPq8MXiJVLiksmOKSjIldZzkebzHuCGzew==",
 289 |       "dev": true,
 290 |       "license": "MIT",
 291 |       "dependencies": {
 292 |         "@typescript-eslint/typescript-estree": "5.62.0",
 293 |         "@typescript-eslint/utils": "5.62.0",
 294 |         "debug": "^4.3.4",
 295 |         "tsutils": "^3.21.0"
 296 |       },
 297 |       "engines": {
 298 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 299 |       },
 300 |       "funding": {
 301 |         "type": "opencollective",
 302 |         "url": "https://opencollective.com/typescript-eslint"
 303 |       },
 304 |       "peerDependencies": {
 305 |         "eslint": "*"
 306 |       },
 307 |       "peerDependenciesMeta": {
 308 |         "typescript": {
 309 |           "optional": true
 310 |         }
 311 |       }
 312 |     },
 313 |     "node_modules/@typescript-eslint/types": {
 314 |       "version": "5.62.0",
 315 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/types/-/types-5.62.0.tgz",
 316 |       "integrity": "sha512-87NVngcbVXUahrRTqIK27gD2t5Cu1yuCXxbLcFtCzZGlfyVWWh8mLHkoxzjsB6DDNnvdL+fW8MiwPEJyGJQDgQ==",
 317 |       "dev": true,
 318 |       "license": "MIT",
 319 |       "engines": {
 320 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 321 |       },
 322 |       "funding": {
 323 |         "type": "opencollective",
 324 |         "url": "https://opencollective.com/typescript-eslint"
 325 |       }
 326 |     },
 327 |     "node_modules/@typescript-eslint/typescript-estree": {
 328 |       "version": "5.62.0",
 329 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/typescript-estree/-/typescript-estree-5.62.0.tgz",
 330 |       "integrity": "sha512-CmcQ6uY7b9y694lKdRB8FEel7JbU/40iSAPomu++SjLMntB+2Leay2LO6i8VnJk58MtE9/nQSFIH6jpyRWyYzA==",
 331 |       "dev": true,
 332 |       "license": "BSD-2-Clause",
 333 |       "dependencies": {
 334 |         "@typescript-eslint/types": "5.62.0",
 335 |         "@typescript-eslint/visitor-keys": "5.62.0",
 336 |         "debug": "^4.3.4",
 337 |         "globby": "^11.1.0",
 338 |         "is-glob": "^4.0.3",
 339 |         "semver": "^7.3.7",
 340 |         "tsutils": "^3.21.0"
 341 |       },
 342 |       "engines": {
 343 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 344 |       },
 345 |       "funding": {
 346 |         "type": "opencollective",
 347 |         "url": "https://opencollective.com/typescript-eslint"
 348 |       },
 349 |       "peerDependenciesMeta": {
 350 |         "typescript": {
 351 |           "optional": true
 352 |         }
 353 |       }
 354 |     },
 355 |     "node_modules/@typescript-eslint/utils": {
 356 |       "version": "5.62.0",
 357 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/utils/-/utils-5.62.0.tgz",
 358 |       "integrity": "sha512-n8oxjeb5aIbPFEtmQxQYOLI0i9n5ySBEY/ZEHHZqKQSFnxio1rv6dthascc9dLuwrL0RC5mPCxB7vnAVGAYWAQ==",
 359 |       "dev": true,
 360 |       "license": "MIT",
 361 |       "dependencies": {
 362 |         "@eslint-community/eslint-utils": "^4.2.0",
 363 |         "@types/json-schema": "^7.0.9",
 364 |         "@types/semver": "^7.3.12",
 365 |         "@typescript-eslint/scope-manager": "5.62.0",
 366 |         "@typescript-eslint/types": "5.62.0",
 367 |         "@typescript-eslint/typescript-estree": "5.62.0",
 368 |         "eslint-scope": "^5.1.1",
 369 |         "semver": "^7.3.7"
 370 |       },
 371 |       "engines": {
 372 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 373 |       },
 374 |       "funding": {
 375 |         "type": "opencollective",
 376 |         "url": "https://opencollective.com/typescript-eslint"
 377 |       },
 378 |       "peerDependencies": {
 379 |         "eslint": "^6.0.0 || ^7.0.0 || ^8.0.0"
 380 |       }
 381 |     },
 382 |     "node_modules/@typescript-eslint/visitor-keys": {
 383 |       "version": "5.62.0",
 384 |       "resolved": "https://registry.npmjs.org/@typescript-eslint/visitor-keys/-/visitor-keys-5.62.0.tgz",
 385 |       "integrity": "sha512-07ny+LHRzQXepkGg6w0mFY41fVUNBrL2Roj/++7V1txKugfjm/Ci/qSND03r2RhlJhJYMcTn9AhhSSqQp0Ysyw==",
 386 |       "dev": true,
 387 |       "license": "MIT",
 388 |       "dependencies": {
 389 |         "@typescript-eslint/types": "5.62.0",
 390 |         "eslint-visitor-keys": "^3.3.0"
 391 |       },
 392 |       "engines": {
 393 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 394 |       },
 395 |       "funding": {
 396 |         "type": "opencollective",
 397 |         "url": "https://opencollective.com/typescript-eslint"
 398 |       }
 399 |     },
 400 |     "node_modules/@ungap/structured-clone": {
 401 |       "version": "1.3.1",
 402 |       "resolved": "https://registry.npmjs.org/@ungap/structured-clone/-/structured-clone-1.3.1.tgz",
 403 |       "integrity": "sha512-mUFwbeTqrVgDQxFveS+df2yfap6iuP20NAKAsBt5jDEoOTDew+zwLAOilHCeQJOVSvmgCX4ogqIrA0mnyr08yQ==",
 404 |       "dev": true,
 405 |       "license": "ISC"
 406 |     },
 407 |     "node_modules/acorn": {
 408 |       "version": "8.16.0",
 409 |       "resolved": "https://registry.npmjs.org/acorn/-/acorn-8.16.0.tgz",
 410 |       "integrity": "sha512-UVJyE9MttOsBQIDKw1skb9nAwQuR5wuGD3+82K6JgJlm/Y+KI92oNsMNGZCYdDsVtRHSak0pcV5Dno5+4jh9sw==",
 411 |       "dev": true,
 412 |       "license": "MIT",
 413 |       "bin": {
 414 |         "acorn": "bin/acorn"
 415 |       },
 416 |       "engines": {
 417 |         "node": ">=0.4.0"
 418 |       }
 419 |     },
 420 |     "node_modules/acorn-jsx": {
 421 |       "version": "5.3.2",
 422 |       "resolved": "https://registry.npmjs.org/acorn-jsx/-/acorn-jsx-5.3.2.tgz",
 423 |       "integrity": "sha512-rq9s+JNhf0IChjtDXxllJ7g41oZk5SlXtp0LHwyA5cejwn7vKmKp4pPri6YEePv2PU65sAsegbXtIinmDFDXgQ==",
 424 |       "dev": true,
 425 |       "license": "MIT",
 426 |       "peerDependencies": {
 427 |         "acorn": "^6.0.0 || ^7.0.0 || ^8.0.0"
 428 |       }
 429 |     },
 430 |     "node_modules/ajv": {
 431 |       "version": "6.15.0",
 432 |       "resolved": "https://registry.npmjs.org/ajv/-/ajv-6.15.0.tgz",
 433 |       "integrity": "sha512-fgFx7Hfoq60ytK2c7DhnF8jIvzYgOMxfugjLOSMHjLIPgenqa7S7oaagATUq99mV6IYvN2tRmC0wnTYX6iPbMw==",
 434 |       "dev": true,
 435 |       "license": "MIT",
 436 |       "dependencies": {
 437 |         "fast-deep-equal": "^3.1.1",
 438 |         "fast-json-stable-stringify": "^2.0.0",
 439 |         "json-schema-traverse": "^0.4.1",
 440 |         "uri-js": "^4.2.2"
 441 |       },
 442 |       "funding": {
 443 |         "type": "github",
 444 |         "url": "https://github.com/sponsors/epoberezkin"
 445 |       }
 446 |     },
 447 |     "node_modules/ansi-regex": {
 448 |       "version": "5.0.1",
 449 |       "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-5.0.1.tgz",
 450 |       "integrity": "sha512-quJQXlTSUGL2LH9SUXo8VwsY4soanhgo6LNSm84E1LBcE8s3O0wpdiRzyR9z/ZZJMlMWv37qOOb9pdJlMUEKFQ==",
 451 |       "dev": true,
 452 |       "license": "MIT",
 453 |       "engines": {
 454 |         "node": ">=8"
 455 |       }
 456 |     },
 457 |     "node_modules/ansi-styles": {
 458 |       "version": "4.3.0",
 459 |       "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.3.0.tgz",
 460 |       "integrity": "sha512-zbB9rCJAT1rbjiVDb2hqKFHNYLxgtk8NURxZ3IZwD3F6NtxbXZQCnnSi1Lkx+IDohdPlFp222wVALIheZJQSEg==",
 461 |       "dev": true,
 462 |       "license": "MIT",
 463 |       "dependencies": {
 464 |         "color-convert": "^2.0.1"
 465 |       },
 466 |       "engines": {
 467 |         "node": ">=8"
 468 |       },
 469 |       "funding": {
 470 |         "url": "https://github.com/chalk/ansi-styles?sponsor=1"
 471 |       }
 472 |     },
 473 |     "node_modules/argparse": {
 474 |       "version": "2.0.1",
 475 |       "resolved": "https://registry.npmjs.org/argparse/-/argparse-2.0.1.tgz",
 476 |       "integrity": "sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q==",
 477 |       "dev": true,
 478 |       "license": "Python-2.0"
 479 |     },
 480 |     "node_modules/array-union": {
 481 |       "version": "2.1.0",
 482 |       "resolved": "https://registry.npmjs.org/array-union/-/array-union-2.1.0.tgz",
 483 |       "integrity": "sha512-HGyxoOTYUyCM6stUe6EJgnd4EoewAI7zMdfqO+kGjnlZmBDz/cR5pf8r/cR4Wq60sL/p0IkcjUEEPwS3GFrIyw==",
 484 |       "dev": true,
 485 |       "license": "MIT",
 486 |       "engines": {
 487 |         "node": ">=8"
 488 |       }
 489 |     },
 490 |     "node_modules/asynckit": {
 491 |       "version": "0.4.0",
 492 |       "resolved": "https://registry.npmjs.org/asynckit/-/asynckit-0.4.0.tgz",
 493 |       "integrity": "sha512-Oei9OH4tRh0YqU3GxhX79dM/mwVgvbZJaSNaRk+bshkj0S5cfHcgYakreBjrHwatXKbz+IoIdYLxrKim2MjW0Q==",
 494 |       "dev": true,
 495 |       "license": "MIT"
 496 |     },
 497 |     "node_modules/balanced-match": {
 498 |       "version": "1.0.2",
 499 |       "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-1.0.2.tgz",
 500 |       "integrity": "sha512-3oSeUO0TMV67hN1AmbXsK4yaqU7tjiHlbxRDZOpH0KW9+CeX4bRAaX0Anxt0tx2MrpRpWwQaPwIlISEJhYU5Pw==",
 501 |       "dev": true,
 502 |       "license": "MIT"
 503 |     },
 504 |     "node_modules/brace-expansion": {
 505 |       "version": "1.1.14",
 506 |       "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.14.tgz",
 507 |       "integrity": "sha512-MWPGfDxnyzKU7rNOW9SP/c50vi3xrmrua/+6hfPbCS2ABNWfx24vPidzvC7krjU/RTo235sV776ymlsMtGKj8g==",
 508 |       "dev": true,
 509 |       "license": "MIT",
 510 |       "dependencies": {
 511 |         "balanced-match": "^1.0.0",
 512 |         "concat-map": "0.0.1"
 513 |       }
 514 |     },
 515 |     "node_modules/braces": {
 516 |       "version": "3.0.3",
 517 |       "resolved": "https://registry.npmjs.org/braces/-/braces-3.0.3.tgz",
 518 |       "integrity": "sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==",
 519 |       "dev": true,
 520 |       "license": "MIT",
 521 |       "dependencies": {
 522 |         "fill-range": "^7.1.1"
 523 |       },
 524 |       "engines": {
 525 |         "node": ">=8"
 526 |       }
 527 |     },
 528 |     "node_modules/call-bind-apply-helpers": {
 529 |       "version": "1.0.2",
 530 |       "resolved": "https://registry.npmjs.org/call-bind-apply-helpers/-/call-bind-apply-helpers-1.0.2.tgz",
 531 |       "integrity": "sha512-Sp1ablJ0ivDkSzjcaJdxEunN5/XvksFJ2sMBFfq6x0ryhQV/2b/KwFe21cMpmHtPOSij8K99/wSfoEuTObmuMQ==",
 532 |       "dev": true,
 533 |       "license": "MIT",
 534 |       "dependencies": {
 535 |         "es-errors": "^1.3.0",
 536 |         "function-bind": "^1.1.2"
 537 |       },
 538 |       "engines": {
 539 |         "node": ">= 0.4"
 540 |       }
 541 |     },
 542 |     "node_modules/callsites": {
 543 |       "version": "3.1.0",
 544 |       "resolved": "https://registry.npmjs.org/callsites/-/callsites-3.1.0.tgz",
 545 |       "integrity": "sha512-P8BjAsXvZS+VIDUI11hHCQEv74YT67YUi5JJFNWIqL235sBmjX4+qx9Muvls5ivyNENctx46xQLQ3aTuE7ssaQ==",
 546 |       "dev": true,
 547 |       "license": "MIT",
 548 |       "engines": {
 549 |         "node": ">=6"
 550 |       }
 551 |     },
 552 |     "node_modules/chalk": {
 553 |       "version": "4.1.2",
 554 |       "resolved": "https://registry.npmjs.org/chalk/-/chalk-4.1.2.tgz",
 555 |       "integrity": "sha512-oKnbhFyRIXpUuez8iBMmyEa4nbj4IOQyuhc/wy9kY7/WVPcwIO9VA668Pu8RkO7+0G76SLROeyw9CpQ061i4mA==",
 556 |       "dev": true,
 557 |       "license": "MIT",
 558 |       "dependencies": {
 559 |         "ansi-styles": "^4.1.0",
 560 |         "supports-color": "^7.1.0"
 561 |       },
 562 |       "engines": {
 563 |         "node": ">=10"
 564 |       },
 565 |       "funding": {
 566 |         "url": "https://github.com/chalk/chalk?sponsor=1"
 567 |       }
 568 |     },
 569 |     "node_modules/color-convert": {
 570 |       "version": "2.0.1",
 571 |       "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz",
 572 |       "integrity": "sha512-RRECPsj7iu/xb5oKYcsFHSppFNnsj/52OVTRKb4zP5onXwVF3zVmmToNcOfGC+CRDpfK/U584fMg38ZHCaElKQ==",
 573 |       "dev": true,
 574 |       "license": "MIT",
 575 |       "dependencies": {
 576 |         "color-name": "~1.1.4"
 577 |       },
 578 |       "engines": {
 579 |         "node": ">=7.0.0"
 580 |       }
 581 |     },
 582 |     "node_modules/color-name": {
 583 |       "version": "1.1.4",
 584 |       "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz",
 585 |       "integrity": "sha512-dOy+3AuW3a2wNbZHIuMZpTcgjGuLU/uBL/ubcZF9OXbDo8ff4O8yVp5Bf0efS8uEoYo5q4Fx7dY9OgQGXgAsQA==",
 586 |       "dev": true,
 587 |       "license": "MIT"
 588 |     },
 589 |     "node_modules/combined-stream": {
 590 |       "version": "1.0.8",
 591 |       "resolved": "https://registry.npmjs.org/combined-stream/-/combined-stream-1.0.8.tgz",
 592 |       "integrity": "sha512-FQN4MRfuJeHf7cBbBMJFXhKSDq+2kAArBlmRBvcvFE5BB1HZKXtSFASDhdlz9zOYwxh8lDdnvmMOe/+5cdoEdg==",
 593 |       "dev": true,
 594 |       "license": "MIT",
 595 |       "dependencies": {
 596 |         "delayed-stream": "~1.0.0"
 597 |       },
 598 |       "engines": {
 599 |         "node": ">= 0.8"
 600 |       }
 601 |     },
 602 |     "node_modules/concat-map": {
 603 |       "version": "0.0.1",
 604 |       "resolved": "https://registry.npmjs.org/concat-map/-/concat-map-0.0.1.tgz",
 605 |       "integrity": "sha512-/Srv4dswyQNBfohGpz9o6Yb3Gz3SrUDqBH5rTuhGR7ahtlbYKnVxw2bCFMRljaA7EXHaXZ8wsHdodFvbkhKmqg==",
 606 |       "dev": true,
 607 |       "license": "MIT"
 608 |     },
 609 |     "node_modules/cross-spawn": {
 610 |       "version": "7.0.6",
 611 |       "resolved": "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.6.tgz",
 612 |       "integrity": "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==",
 613 |       "dev": true,
 614 |       "license": "MIT",
 615 |       "dependencies": {
 616 |         "path-key": "^3.1.0",
 617 |         "shebang-command": "^2.0.0",
 618 |         "which": "^2.0.1"
 619 |       },
 620 |       "engines": {
 621 |         "node": ">= 8"
 622 |       }
 623 |     },
 624 |     "node_modules/debug": {
 625 |       "version": "4.4.3",
 626 |       "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.3.tgz",
 627 |       "integrity": "sha512-RGwwWnwQvkVfavKVt22FGLw+xYSdzARwm0ru6DhTVA3umU5hZc28V3kO4stgYryrTlLpuvgI9GiijltAjNbcqA==",
 628 |       "dev": true,
 629 |       "license": "MIT",
 630 |       "dependencies": {
 631 |         "ms": "^2.1.3"
 632 |       },
 633 |       "engines": {
 634 |         "node": ">=6.0"
 635 |       },
 636 |       "peerDependenciesMeta": {
 637 |         "supports-color": {
 638 |           "optional": true
 639 |         }
 640 |       }
 641 |     },
 642 |     "node_modules/deep-is": {
 643 |       "version": "0.1.4",
 644 |       "resolved": "https://registry.npmjs.org/deep-is/-/deep-is-0.1.4.tgz",
 645 |       "integrity": "sha512-oIPzksmTg4/MriiaYGO+okXDT7ztn/w3Eptv/+gSIdMdKsJo0u4CfYNFJPy+4SKMuCqGw2wxnA+URMg3t8a/bQ==",
 646 |       "dev": true,
 647 |       "license": "MIT"
 648 |     },
 649 |     "node_modules/delayed-stream": {
 650 |       "version": "1.0.0",
 651 |       "resolved": "https://registry.npmjs.org/delayed-stream/-/delayed-stream-1.0.0.tgz",
 652 |       "integrity": "sha512-ZySD7Nf91aLB0RxL4KGrKHBXl7Eds1DAmEdcoVawXnLD7SDhpNgtuII2aAkg7a7QS41jxPSZ17p4VdGnMHk3MQ==",
 653 |       "dev": true,
 654 |       "license": "MIT",
 655 |       "engines": {
 656 |         "node": ">=0.4.0"
 657 |       }
 658 |     },
 659 |     "node_modules/dir-glob": {
 660 |       "version": "3.0.1",
 661 |       "resolved": "https://registry.npmjs.org/dir-glob/-/dir-glob-3.0.1.tgz",
 662 |       "integrity": "sha512-WkrWp9GR4KXfKGYzOLmTuGVi1UWFfws377n9cc55/tb6DuqyF6pcQ5AbiHEshaDpY9v6oaSr2XCDidGmMwdzIA==",
 663 |       "dev": true,
 664 |       "license": "MIT",
 665 |       "dependencies": {
 666 |         "path-type": "^4.0.0"
 667 |       },
 668 |       "engines": {
 669 |         "node": ">=8"
 670 |       }
 671 |     },
 672 |     "node_modules/doctrine": {
 673 |       "version": "3.0.0",
 674 |       "resolved": "https://registry.npmjs.org/doctrine/-/doctrine-3.0.0.tgz",
 675 |       "integrity": "sha512-yS+Q5i3hBf7GBkd4KG8a7eBNNWNGLTaEwwYWUijIYM7zrlYDM0BFXHjjPWlWZ1Rg7UaddZeIDmi9jF3HmqiQ2w==",
 676 |       "dev": true,
 677 |       "license": "Apache-2.0",
 678 |       "dependencies": {
 679 |         "esutils": "^2.0.2"
 680 |       },
 681 |       "engines": {
 682 |         "node": ">=6.0.0"
 683 |       }
 684 |     },
 685 |     "node_modules/dunder-proto": {
 686 |       "version": "1.0.1",
 687 |       "resolved": "https://registry.npmjs.org/dunder-proto/-/dunder-proto-1.0.1.tgz",
 688 |       "integrity": "sha512-KIN/nDJBQRcXw0MLVhZE9iQHmG68qAVIBg9CqmUYjmQIhgij9U5MFvrqkUL5FbtyyzZuOeOt0zdeRe4UY7ct+A==",
 689 |       "dev": true,
 690 |       "license": "MIT",
 691 |       "dependencies": {
 692 |         "call-bind-apply-helpers": "^1.0.1",
 693 |         "es-errors": "^1.3.0",
 694 |         "gopd": "^1.2.0"
 695 |       },
 696 |       "engines": {
 697 |         "node": ">= 0.4"
 698 |       }
 699 |     },
 700 |     "node_modules/es-define-property": {
 701 |       "version": "1.0.1",
 702 |       "resolved": "https://registry.npmjs.org/es-define-property/-/es-define-property-1.0.1.tgz",
 703 |       "integrity": "sha512-e3nRfgfUZ4rNGL232gUgX06QNyyez04KdjFrF+LTRoOXmrOgFKDg4BCdsjW8EnT69eqdYGmRpJwiPVYNrCaW3g==",
 704 |       "dev": true,
 705 |       "license": "MIT",
 706 |       "engines": {
 707 |         "node": ">= 0.4"
 708 |       }
 709 |     },
 710 |     "node_modules/es-errors": {
 711 |       "version": "1.3.0",
 712 |       "resolved": "https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz",
 713 |       "integrity": "sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==",
 714 |       "dev": true,
 715 |       "license": "MIT",
 716 |       "engines": {
 717 |         "node": ">= 0.4"
 718 |       }
 719 |     },
 720 |     "node_modules/es-object-atoms": {
 721 |       "version": "1.1.1",
 722 |       "resolved": "https://registry.npmjs.org/es-object-atoms/-/es-object-atoms-1.1.1.tgz",
 723 |       "integrity": "sha512-FGgH2h8zKNim9ljj7dankFPcICIK9Cp5bm+c2gQSYePhpaG5+esrLODihIorn+Pe6FGJzWhXQotPv73jTaldXA==",
 724 |       "dev": true,
 725 |       "license": "MIT",
 726 |       "dependencies": {
 727 |         "es-errors": "^1.3.0"
 728 |       },
 729 |       "engines": {
 730 |         "node": ">= 0.4"
 731 |       }
 732 |     },
 733 |     "node_modules/es-set-tostringtag": {
 734 |       "version": "2.1.0",
 735 |       "resolved": "https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.1.0.tgz",
 736 |       "integrity": "sha512-j6vWzfrGVfyXxge+O0x5sh6cvxAog0a/4Rdd2K36zCMV5eJ+/+tOAngRO8cODMNWbVRdVlmGZQL2YS3yR8bIUA==",
 737 |       "dev": true,
 738 |       "license": "MIT",
 739 |       "dependencies": {
 740 |         "es-errors": "^1.3.0",
 741 |         "get-intrinsic": "^1.2.6",
 742 |         "has-tostringtag": "^1.0.2",
 743 |         "hasown": "^2.0.2"
 744 |       },
 745 |       "engines": {
 746 |         "node": ">= 0.4"
 747 |       }
 748 |     },
 749 |     "node_modules/escape-string-regexp": {
 750 |       "version": "4.0.0",
 751 |       "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz",
 752 |       "integrity": "sha512-TtpcNJ3XAzx3Gq8sWRzJaVajRs0uVxA2YAkdb1jm2YkPz4G6egUFAyA3n5vtEIZefPk5Wa4UXbKuS5fKkJWdgA==",
 753 |       "dev": true,
 754 |       "license": "MIT",
 755 |       "engines": {
 756 |         "node": ">=10"
 757 |       },
 758 |       "funding": {
 759 |         "url": "https://github.com/sponsors/sindresorhus"
 760 |       }
 761 |     },
 762 |     "node_modules/eslint": {
 763 |       "version": "8.57.1",
 764 |       "resolved": "https://registry.npmjs.org/eslint/-/eslint-8.57.1.tgz",
 765 |       "integrity": "sha512-ypowyDxpVSYpkXr9WPv2PAZCtNip1Mv5KTW0SCurXv/9iOpcrH9PaqUElksqEB6pChqHGDRCFTyrZlGhnLNGiA==",
 766 |       "deprecated": "This version is no longer supported. Please see https://eslint.org/version-support for other options.",
 767 |       "dev": true,
 768 |       "license": "MIT",
 769 |       "dependencies": {
 770 |         "@eslint-community/eslint-utils": "^4.2.0",
 771 |         "@eslint-community/regexpp": "^4.6.1",
 772 |         "@eslint/eslintrc": "^2.1.4",
 773 |         "@eslint/js": "8.57.1",
 774 |         "@humanwhocodes/config-array": "^0.13.0",
 775 |         "@humanwhocodes/module-importer": "^1.0.1",
 776 |         "@nodelib/fs.walk": "^1.2.8",
 777 |         "@ungap/structured-clone": "^1.2.0",
 778 |         "ajv": "^6.12.4",
 779 |         "chalk": "^4.0.0",
 780 |         "cross-spawn": "^7.0.2",
 781 |         "debug": "^4.3.2",
 782 |         "doctrine": "^3.0.0",
 783 |         "escape-string-regexp": "^4.0.0",
 784 |         "eslint-scope": "^7.2.2",
 785 |         "eslint-visitor-keys": "^3.4.3",
 786 |         "espree": "^9.6.1",
 787 |         "esquery": "^1.4.2",
 788 |         "esutils": "^2.0.2",
 789 |         "fast-deep-equal": "^3.1.3",
 790 |         "file-entry-cache": "^6.0.1",
 791 |         "find-up": "^5.0.0",
 792 |         "glob-parent": "^6.0.2",
 793 |         "globals": "^13.19.0",
 794 |         "graphemer": "^1.4.0",
 795 |         "ignore": "^5.2.0",
 796 |         "imurmurhash": "^0.1.4",
 797 |         "is-glob": "^4.0.0",
 798 |         "is-path-inside": "^3.0.3",
 799 |         "js-yaml": "^4.1.0",
 800 |         "json-stable-stringify-without-jsonify": "^1.0.1",
 801 |         "levn": "^0.4.1",
 802 |         "lodash.merge": "^4.6.2",
 803 |         "minimatch": "^3.1.2",
 804 |         "natural-compare": "^1.4.0",
 805 |         "optionator": "^0.9.3",
 806 |         "strip-ansi": "^6.0.1",
 807 |         "text-table": "^0.2.0"
 808 |       },
 809 |       "bin": {
 810 |         "eslint": "bin/eslint.js"
 811 |       },
 812 |       "engines": {
 813 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 814 |       },
 815 |       "funding": {
 816 |         "url": "https://opencollective.com/eslint"
 817 |       }
 818 |     },
 819 |     "node_modules/eslint-scope": {
 820 |       "version": "5.1.1",
 821 |       "resolved": "https://registry.npmjs.org/eslint-scope/-/eslint-scope-5.1.1.tgz",
 822 |       "integrity": "sha512-2NxwbF/hZ0KpepYN0cNbo+FN6XoK7GaHlQhgx/hIZl6Va0bF45RQOOwhLIy8lQDbuCiadSLCBnH2CFYquit5bw==",
 823 |       "dev": true,
 824 |       "license": "BSD-2-Clause",
 825 |       "dependencies": {
 826 |         "esrecurse": "^4.3.0",
 827 |         "estraverse": "^4.1.1"
 828 |       },
 829 |       "engines": {
 830 |         "node": ">=8.0.0"
 831 |       }
 832 |     },
 833 |     "node_modules/eslint-visitor-keys": {
 834 |       "version": "3.4.3",
 835 |       "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-3.4.3.tgz",
 836 |       "integrity": "sha512-wpc+LXeiyiisxPlEkUzU6svyS1frIO3Mgxj1fdy7Pm8Ygzguax2N3Fa/D/ag1WqbOprdI+uY6wMUl8/a2G+iag==",
 837 |       "dev": true,
 838 |       "license": "Apache-2.0",
 839 |       "engines": {
 840 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 841 |       },
 842 |       "funding": {
 843 |         "url": "https://opencollective.com/eslint"
 844 |       }
 845 |     },
 846 |     "node_modules/eslint/node_modules/eslint-scope": {
 847 |       "version": "7.2.2",
 848 |       "resolved": "https://registry.npmjs.org/eslint-scope/-/eslint-scope-7.2.2.tgz",
 849 |       "integrity": "sha512-dOt21O7lTMhDM+X9mB4GX+DZrZtCUJPL/wlcTqxyrx5IvO0IYtILdtrQGQp+8n5S0gwSVmOf9NQrjMOgfQZlIg==",
 850 |       "dev": true,
 851 |       "license": "BSD-2-Clause",
 852 |       "dependencies": {
 853 |         "esrecurse": "^4.3.0",
 854 |         "estraverse": "^5.2.0"
 855 |       },
 856 |       "engines": {
 857 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 858 |       },
 859 |       "funding": {
 860 |         "url": "https://opencollective.com/eslint"
 861 |       }
 862 |     },
 863 |     "node_modules/eslint/node_modules/estraverse": {
 864 |       "version": "5.3.0",
 865 |       "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
 866 |       "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
 867 |       "dev": true,
 868 |       "license": "BSD-2-Clause",
 869 |       "engines": {
 870 |         "node": ">=4.0"
 871 |       }
 872 |     },
 873 |     "node_modules/espree": {
 874 |       "version": "9.6.1",
 875 |       "resolved": "https://registry.npmjs.org/espree/-/espree-9.6.1.tgz",
 876 |       "integrity": "sha512-oruZaFkjorTpF32kDSI5/75ViwGeZginGGy2NoOSg3Q9bnwlnmDm4HLnkl0RE3n+njDXR037aY1+x58Z/zFdwQ==",
 877 |       "dev": true,
 878 |       "license": "BSD-2-Clause",
 879 |       "dependencies": {
 880 |         "acorn": "^8.9.0",
 881 |         "acorn-jsx": "^5.3.2",
 882 |         "eslint-visitor-keys": "^3.4.1"
 883 |       },
 884 |       "engines": {
 885 |         "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
 886 |       },
 887 |       "funding": {
 888 |         "url": "https://opencollective.com/eslint"
 889 |       }
 890 |     },
 891 |     "node_modules/esquery": {
 892 |       "version": "1.7.0",
 893 |       "resolved": "https://registry.npmjs.org/esquery/-/esquery-1.7.0.tgz",
 894 |       "integrity": "sha512-Ap6G0WQwcU/LHsvLwON1fAQX9Zp0A2Y6Y/cJBl9r/JbW90Zyg4/zbG6zzKa2OTALELarYHmKu0GhpM5EO+7T0g==",
 895 |       "dev": true,
 896 |       "license": "BSD-3-Clause",
 897 |       "dependencies": {
 898 |         "estraverse": "^5.1.0"
 899 |       },
 900 |       "engines": {
 901 |         "node": ">=0.10"
 902 |       }
 903 |     },
 904 |     "node_modules/esquery/node_modules/estraverse": {
 905 |       "version": "5.3.0",
 906 |       "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
 907 |       "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
 908 |       "dev": true,
 909 |       "license": "BSD-2-Clause",
 910 |       "engines": {
 911 |         "node": ">=4.0"
 912 |       }
 913 |     },
 914 |     "node_modules/esrecurse": {
 915 |       "version": "4.3.0",
 916 |       "resolved": "https://registry.npmjs.org/esrecurse/-/esrecurse-4.3.0.tgz",
 917 |       "integrity": "sha512-KmfKL3b6G+RXvP8N1vr3Tq1kL/oCFgn2NYXEtqP8/L3pKapUA4G8cFVaoF3SU323CD4XypR/ffioHmkti6/Tag==",
 918 |       "dev": true,
 919 |       "license": "BSD-2-Clause",
 920 |       "dependencies": {
 921 |         "estraverse": "^5.2.0"
 922 |       },
 923 |       "engines": {
 924 |         "node": ">=4.0"
 925 |       }
 926 |     },
 927 |     "node_modules/esrecurse/node_modules/estraverse": {
 928 |       "version": "5.3.0",
 929 |       "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
 930 |       "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
 931 |       "dev": true,
 932 |       "license": "BSD-2-Clause",
 933 |       "engines": {
 934 |         "node": ">=4.0"
 935 |       }
 936 |     },
 937 |     "node_modules/estraverse": {
 938 |       "version": "4.3.0",
 939 |       "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-4.3.0.tgz",
 940 |       "integrity": "sha512-39nnKffWz8xN1BU/2c79n9nB9HDzo0niYUqx6xyqUnyoAnQyyWpOTdZEeiCch8BBu515t4wp9ZmgVfVhn9EBpw==",
 941 |       "dev": true,
 942 |       "license": "BSD-2-Clause",
 943 |       "engines": {
 944 |         "node": ">=4.0"
 945 |       }
 946 |     },
 947 |     "node_modules/esutils": {
 948 |       "version": "2.0.3",
 949 |       "resolved": "https://registry.npmjs.org/esutils/-/esutils-2.0.3.tgz",
 950 |       "integrity": "sha512-kVscqXk4OCp68SZ0dkgEKVi6/8ij300KBWTJq32P/dYeWTSwK41WyTxalN1eRmA5Z9UU/LX9D7FWSmV9SAYx6g==",
 951 |       "dev": true,
 952 |       "license": "BSD-2-Clause",
 953 |       "engines": {
 954 |         "node": ">=0.10.0"
 955 |       }
 956 |     },
 957 |     "node_modules/fast-deep-equal": {
 958 |       "version": "3.1.3",
 959 |       "resolved": "https://registry.npmjs.org/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz",
 960 |       "integrity": "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q==",
 961 |       "dev": true,
 962 |       "license": "MIT"
 963 |     },
 964 |     "node_modules/fast-glob": {
 965 |       "version": "3.3.3",
 966 |       "resolved": "https://registry.npmjs.org/fast-glob/-/fast-glob-3.3.3.tgz",
 967 |       "integrity": "sha512-7MptL8U0cqcFdzIzwOTHoilX9x5BrNqye7Z/LuC7kCMRio1EMSyqRK3BEAUD7sXRq4iT4AzTVuZdhgQ2TCvYLg==",
 968 |       "dev": true,
 969 |       "license": "MIT",
 970 |       "dependencies": {
 971 |         "@nodelib/fs.stat": "^2.0.2",
 972 |         "@nodelib/fs.walk": "^1.2.3",
 973 |         "glob-parent": "^5.1.2",
 974 |         "merge2": "^1.3.0",
 975 |         "micromatch": "^4.0.8"
 976 |       },
 977 |       "engines": {
 978 |         "node": ">=8.6.0"
 979 |       }
 980 |     },
 981 |     "node_modules/fast-glob/node_modules/glob-parent": {
 982 |       "version": "5.1.2",
 983 |       "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
 984 |       "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
 985 |       "dev": true,
 986 |       "license": "ISC",
 987 |       "dependencies": {
 988 |         "is-glob": "^4.0.1"
 989 |       },
 990 |       "engines": {
 991 |         "node": ">= 6"
 992 |       }
 993 |     },
 994 |     "node_modules/fast-json-stable-stringify": {
 995 |       "version": "2.1.0",
 996 |       "resolved": "https://registry.npmjs.org/fast-json-stable-stringify/-/fast-json-stable-stringify-2.1.0.tgz",
 997 |       "integrity": "sha512-lhd/wF+Lk98HZoTCtlVraHtfh5XYijIjalXck7saUtuanSDyLMxnHhSXEDJqHxD7msR8D0uCmqlkwjCV8xvwHw==",
 998 |       "dev": true,
 999 |       "license": "MIT"
1000 |     },


[File truncated: showing 1000 of 2074 total lines. The file is too large and may exhaust the context window if read in full.]
</file_content>

<file_content path="vscode-extension/package.json">
 1 | {
 2 |   "name": "reposense",
 3 |   "displayName": "RepoSense",
 4 |   "description": "Analyze workspace repositories and get health scores",
 5 |   "version": "0.0.1",
 6 |   "engines": {
 7 |     "vscode": "^1.74.0"
 8 |   },
 9 |   "categories": [
10 |     "Other"
11 |   ],
12 |   "activationEvents": [
13 |     "onView:reposense-sidebar"
14 |   ],
15 |   "main": "./out/extension.js",
16 |   "contributes": {
17 |     "commands": [
18 |       {
19 |         "command": "reposense.refresh",
20 |         "title": "Refresh Analysis",
21 |         "icon": "$(refresh)"
22 |       },
23 |       {
24 |         "command": "reposense.openInBrowser",
25 |         "title": "RepoSense: Open in Browser",
26 |         "icon": "$(globe)"
27 |       }
28 |     ],
29 |     "viewsContainers": {
30 |       "activitybar": [
31 |         {
32 |           "id": "reposense-sidebar-view",
33 |           "title": "RepoSense",
34 |           "icon": "media/icon.svg"
35 |         }
36 |       ]
37 |     },
38 |     "views": {
39 |       "reposense-sidebar-view": [
40 |         {
41 |           "type": "webview",
42 |           "id": "reposense-sidebar",
43 |           "name": "RepoSense",
44 |           "icon": "media/icon.svg",
45 |           "contextualTitle": "RepoSense"
46 |         }
47 |       ]
48 |     },
49 |     "menus": {
50 |       "view/title": [
51 |         {
52 |           "command": "reposense.refresh",
53 |           "when": "view == reposense-sidebar",
54 |           "group": "navigation"
55 |         }
56 |       ]
57 |     },
58 |     "configuration": {
59 |       "title": "RepoSense",
60 |       "properties": {
61 |         "reposense.backendUrl": {
62 |           "type": "string",
63 |           "default": "http://localhost:8000",
64 |           "description": "URL of the RepoSense backend API server"
65 |         },
66 |         "reposense.requestTimeoutMs": {
67 |           "type": "number",
68 |           "default": 30000,
69 |           "description": "HTTP request timeout in milliseconds"
70 |         },
71 |         "reposense.pollingIntervalMs": {
72 |           "type": "number",
73 |           "default": 2000,
74 |           "description": "How often to poll for job results (milliseconds)"
75 |         }
76 |       }
77 |     }
78 |   },
79 |   "scripts": {
80 |     "vscode:prepublish": "npm run compile",
81 |     "compile": "tsc -p ./",
82 |     "watch": "tsc -watch -p ./",
83 |     "pretest": "npm run compile && npm run lint",
84 |     "lint": "eslint src --ext ts"
85 |   },
86 |   "devDependencies": {
87 |     "@types/vscode": "^1.74.0",
88 |     "@types/node": "16.x",
89 |     "@types/node-fetch": "^2.6.2",
90 |     "@typescript-eslint/eslint-plugin": "^5.45.0",
91 |     "@typescript-eslint/parser": "^5.45.0",
92 |     "eslint": "^8.28.0",
93 |     "typescript": "^4.9.3"
94 |   },
95 |   "dependencies": {
96 |     "node-fetch": "^2.7.0"
97 |   }
98 | }

</file_content>

<file_content path="vscode-extension/README.md">
  1 | # RepoSense
  2 | 
  3 | A VS Code extension that analyzes your workspace repository and provides health scores through integration with a backend analysis service.
  4 | 
  5 | ## Features
  6 | 
  7 | - **Webview Sidebar**: Access RepoSense functionality through a dedicated sidebar panel
  8 | - **Workspace Analysis**: Analyze your current workspace with a single click
  9 | - **Real-time Progress**: See live updates as the analysis progresses
 10 | - **Health Score**: Get a comprehensive health score for your repository
 11 | - **Backend Integration**: Communicates with a local analysis service at `http://localhost:8000`
 12 | 
 13 | ## Requirements
 14 | 
 15 | - VS Code version 1.74.0 or higher
 16 | - RepoSense backend service running on `http://localhost:8000`
 17 | 
 18 | ## Installation
 19 | 
 20 | ### From Source
 21 | 
 22 | 1. Clone this repository
 23 | 2. Navigate to the extension directory:
 24 |    ```bash
 25 |    cd vscode-extension
 26 |    ```
 27 | 3. Install dependencies:
 28 |    ```bash
 29 |    npm install
 30 |    ```
 31 | 4. Compile the extension:
 32 |    ```bash
 33 |    npm run compile
 34 |    ```
 35 | 5. Press `F5` to open a new VS Code window with the extension loaded
 36 | 
 37 | ### From VSIX Package
 38 | 
 39 | 1. Download the `.vsix` file
 40 | 2. Open VS Code
 41 | 3. Go to Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`)
 42 | 4. Click the `...` menu at the top of the Extensions view
 43 | 5. Select "Install from VSIX..."
 44 | 6. Choose the downloaded `.vsix` file
 45 | 
 46 | ## Usage
 47 | 
 48 | 1. **Start the Backend Service**: Ensure the RepoSense backend is running on `http://localhost:8000`
 49 | 
 50 | 2. **Open the Sidebar**: Click the RepoSense icon in the Activity Bar (left sidebar)
 51 | 
 52 | 3. **Analyze Workspace**: 
 53 |    - Click the "Analyze Workspace" button
 54 |    - The extension will send your workspace path to the backend
 55 |    - Watch real-time progress updates as the analysis runs
 56 |    - View the final health score when complete
 57 | 
 58 | ## How It Works
 59 | 
 60 | 1. When you click "Analyze Workspace", the extension:
 61 |    - Reads your current workspace folder path
 62 |    - Sends a POST request to `http://localhost:8000/analyze` with the path
 63 |    - Receives a `job_id` in response
 64 | 
 65 | 2. The extension then polls `http://localhost:8000/results/{job_id}` every 3 seconds to:
 66 |    - Check the analysis status
 67 |    - Display progress updates (e.g., "✓ Architect complete...")
 68 |    - Show the final health score when analysis is complete
 69 | 
 70 | ## API Endpoints
 71 | 
 72 | The extension expects the following backend endpoints:
 73 | 
 74 | ### POST /analyze
 75 | Request:
 76 | ```json
 77 | {
 78 |   "local_path": "/path/to/workspace"
 79 | }
 80 | ```
 81 | 
 82 | Response:
 83 | ```json
 84 | {
 85 |   "job_id": "unique-job-id"
 86 | }
 87 | ```
 88 | 
 89 | ### GET /results/{job_id}
 90 | Response (in progress):
 91 | ```json
 92 | {
 93 |   "job_id": "unique-job-id",
 94 |   "status": "in_progress",
 95 |   "progress": {
 96 |     "architect": true
 97 |   }
 98 | }
 99 | ```
100 | 
101 | Response (complete):
102 | ```json
103 | {
104 |   "job_id": "unique-job-id",
105 |   "status": "completed",
106 |   "health_score": 85
107 | }
108 | ```
109 | 
110 | ## Development
111 | 
112 | ### Building
113 | 
114 | ```bash
115 | npm run compile
116 | ```
117 | 
118 | ### Watching for Changes
119 | 
120 | ```bash
121 | npm run watch
122 | ```
123 | 
124 | ### Debugging
125 | 
126 | 1. Open the extension folder in VS Code
127 | 2. Press `F5` to start debugging
128 | 3. A new Extension Development Host window will open with the extension loaded
129 | 
130 | ## Extension Settings
131 | 
132 | This extension contributes the following:
133 | 
134 | - `reposense-sidebar`: Webview sidebar panel for RepoSense analysis
135 | 
136 | ## Known Issues
137 | 
138 | - Backend service must be running on `http://localhost:8000` before using the extension
139 | - No configuration options for custom backend URLs (coming in future versions)
140 | 
141 | ## Release Notes
142 | 
143 | ### 0.0.1
144 | 
145 | Initial release of RepoSense extension:
146 | - Workspace analysis with backend integration
147 | - Real-time progress updates
148 | - Health score display
149 | - Polling-based status checking
150 | 
151 | ## License
152 | 
153 | See LICENSE file for details.

</file_content>

<file_content path="vscode-extension/SETUP.md">
  1 | # RepoSense VSCode Extension Setup Guide
  2 | 
  3 | This guide explains how to set up and connect the RepoSense VSCode extension to the backend API.
  4 | 
  5 | ## Prerequisites
  6 | 
  7 | 1. **Backend Running**: The RepoSense backend must be running on `http://localhost:8000` (default)
  8 | 2. **Node.js**: Version 16.x or higher
  9 | 3. **VSCode**: Version 1.74.0 or higher
 10 | 
 11 | ## Backend Setup
 12 | 
 13 | ### 1. Configure Backend Environment
 14 | 
 15 | Navigate to the backend directory and create a `.env` file:
 16 | 
 17 | ```bash
 18 | cd backend
 19 | cp .env.example .env
 20 | ```
 21 | 
 22 | Edit `.env` and add your WatsonX credentials:
 23 | 
 24 | ```env
 25 | WATSONX_API_KEY=your-actual-api-key
 26 | WATSONX_PROJECT_ID=your-actual-project-id
 27 | ```
 28 | 
 29 | ### 2. Update CORS Settings (Important!)
 30 | 
 31 | The backend needs to allow requests from the VSCode extension. Update the `CORS_ORIGINS` in your `.env` file:
 32 | 
 33 | ```env
 34 | # Add vscode-webview:// protocol for VSCode extension
 35 | CORS_ORIGINS=http://localhost:3000,http://localhost:5173,vscode-webview://,http://localhost:*
 36 | ```
 37 | 
 38 | Or modify `backend/src/config.py` to allow all origins during development:
 39 | 
 40 | ```python
 41 | cors_origins: str = "*"  # Allow all origins (development only!)
 42 | ```
 43 | 
 44 | ### 3. Install Backend Dependencies
 45 | 
 46 | ```bash
 47 | cd backend
 48 | pip install -r requirements.txt
 49 | ```
 50 | 
 51 | ### 4. Start the Backend
 52 | 
 53 | ```bash
 54 | cd backend
 55 | python -m src.main
 56 | ```
 57 | 
 58 | Or using uvicorn directly:
 59 | 
 60 | ```bash
 61 | cd backend
 62 | uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
 63 | ```
 64 | 
 65 | Verify the backend is running by visiting: http://localhost:8000
 66 | 
 67 | You should see:
 68 | ```json
 69 | {
 70 |   "service": "RepoSense API",
 71 |   "status": "running",
 72 |   "version": "1.0.0"
 73 | }
 74 | ```
 75 | 
 76 | ## Extension Setup
 77 | 
 78 | ### 1. Install Extension Dependencies
 79 | 
 80 | ```bash
 81 | cd vscode-extension
 82 | npm install
 83 | ```
 84 | 
 85 | ### 2. Configure Backend URL (Optional)
 86 | 
 87 | If your backend runs on a different port, edit `vscode-extension/src/config.ts`:
 88 | 
 89 | ```typescript
 90 | export const defaultConfig: ExtensionConfig = {
 91 |     backendUrl: 'http://localhost:8000',  // Change this if needed
 92 |     pollingIntervalMs: 3000,
 93 |     requestTimeoutMs: 30000
 94 | };
 95 | ```
 96 | 
 97 | ### 3. Compile the Extension
 98 | 
 99 | ```bash
100 | cd vscode-extension
101 | npm run compile
102 | ```
103 | 
104 | ### 4. Run the Extension
105 | 
106 | 1. Open the `vscode-extension` folder in VSCode
107 | 2. Press `F5` to start debugging
108 | 3. A new VSCode window will open with the extension loaded
109 | 
110 | ## Using the Extension
111 | 
112 | ### 1. Open the RepoSense Sidebar
113 | 
114 | - Click the RepoSense icon in the Activity Bar (left sidebar)
115 | - Or use Command Palette: `View: Show RepoSense`
116 | 
117 | ### 2. Analyze Your Workspace
118 | 
119 | 1. Open a workspace/folder in VSCode
120 | 2. Click the "Analyze Workspace" button in the RepoSense sidebar
121 | 3. Watch the progress as the analysis runs
122 | 4. View the results when complete
123 | 
124 | ### 3. Understanding the Results
125 | 
126 | The extension displays:
127 | - **Health Score**: Overall score (0-100) with letter grade (A-F)
128 | - **Breakdown**: Scores for Quality, Security, Documentation, and Architecture
129 | - **Top Priorities**: Key areas to focus on for improvement
130 | - **Summary**: AI-generated summary of the codebase health
131 | - **Analysis Details**: Counts of findings, issues, and recommendations
132 | 
133 | ## API Endpoints Used
134 | 
135 | The extension communicates with these backend endpoints:
136 | 
137 | ### POST /analyze
138 | Start a new analysis job.
139 | 
140 | **Request:**
141 | ```json
142 | {
143 |   "local_path": "/path/to/workspace"
144 | }
145 | ```
146 | 
147 | **Response:**
148 | ```json
149 | {
150 |   "type": "request",
151 |   "job_id": "uuid-string",
152 |   "progress": [
153 |     {
154 |       "name": "Parsing codebase",
155 |       "status": "active",
156 |       "files_processed": 10,
157 |       "files_total": 50
158 |     }
159 |   ],
160 |   "payload": null
161 | }
162 | ```
163 | 
164 | ### GET /jobs/{job_id}
165 | Poll for job status and results.
166 | 
167 | **Response Types:**
168 | 
169 | 1. **In Progress** (`type: "request"`):
170 | ```json
171 | {
172 |   "type": "request",
173 |   "job_id": "uuid",
174 |   "progress": [...],
175 |   "payload": null
176 | }
177 | ```
178 | 
179 | 2. **Completed** (`type: "result"`):
180 | ```json
181 | {
182 |   "type": "result",
183 |   "job_id": "uuid",
184 |   "progress": [...],
185 |   "payload": {
186 |     "score": {
187 |       "score": 85,
188 |       "grade": "B",
189 |       "breakdown": {...},
190 |       "summary": "...",
191 |       "top_priorities": [...]
192 |     },
193 |     "architecture": {...},
194 |     "review": {...},
195 |     "docs": {...},
196 |     "security": {...}
197 |   }
198 | }
199 | ```
200 | 
201 | 3. **Failed** (`type: "error"`):
202 | ```json
203 | {
204 |   "type": "error",
205 |   "job_id": "uuid",
206 |   "progress": [...],
207 |   "payload": {
208 |     "code": "PARSE_FAILED",
209 |     "message": "Error details",
210 |     "stage": "Parsing codebase"
211 |   }
212 | }
213 | ```
214 | 
215 | ## Troubleshooting
216 | 
217 | ### Extension Can't Connect to Backend
218 | 
219 | **Error:** "Failed to start analysis: Failed to fetch"
220 | 
221 | **Solutions:**
222 | 1. Verify backend is running: `curl http://localhost:8000`
223 | 2. Check CORS configuration in backend `.env`
224 | 3. Check browser console in VSCode DevTools: `Help > Toggle Developer Tools`
225 | 
226 | ### CORS Errors
227 | 
228 | **Error:** "Access to fetch at 'http://localhost:8000/analyze' from origin 'vscode-webview://...' has been blocked by CORS policy"
229 | 
230 | **Solution:**
231 | Update backend CORS settings to allow VSCode webview origins:
232 | ```env
233 | CORS_ORIGINS=*
234 | ```
235 | 
236 | Or specifically:
237 | ```env
238 | CORS_ORIGINS=vscode-webview://,http://localhost:*
239 | ```
240 | 
241 | ### Backend Not Starting
242 | 
243 | **Error:** "ValidationError: watsonx_api_key"
244 | 
245 | **Solution:**
246 | Ensure your `.env` file has valid WatsonX credentials:
247 | ```env
248 | WATSONX_API_KEY=your-actual-key-here
249 | WATSONX_PROJECT_ID=your-actual-project-id
250 | ```
251 | 
252 | ### Analysis Fails Immediately
253 | 
254 | **Error:** "Path does not exist" or "Path is not a directory"
255 | 
256 | **Solution:**
257 | The extension sends the workspace folder path. Ensure:
258 | 1. You have a folder open in VSCode (not just files)
259 | 2. The backend has permission to read the directory
260 | 3. The path is valid on your system
261 | 
262 | ### Polling Doesn't Stop
263 | 
264 | **Issue:** Extension keeps polling even after completion
265 | 
266 | **Solution:**
267 | This is a bug. Reload the VSCode window: `Developer: Reload Window`
268 | 
269 | ## Development Tips
270 | 
271 | ### Debugging the Extension
272 | 
273 | 1. Open `vscode-extension` in VSCode
274 | 2. Set breakpoints in TypeScript files
275 | 3. Press `F5` to start debugging
276 | 4. Use Debug Console to inspect variables
277 | 
278 | ### Viewing Network Requests
279 | 
280 | 1. In the Extension Development Host window
281 | 2. Open DevTools: `Help > Toggle Developer Tools`
282 | 3. Go to Network tab
283 | 4. Filter by "localhost:8000"
284 | 
285 | ### Modifying the UI
286 | 
287 | Edit the HTML in `SidebarProvider.ts` method `_getHtmlForWebview()`:
288 | - Styles are inline using VSCode CSS variables
289 | - JavaScript uses the VSCode API via `acquireVsCodeApi()`
290 | 
291 | ### Testing Backend Endpoints
292 | 
293 | Use curl or Postman:
294 | 
295 | ```bash
296 | # Start analysis
297 | curl -X POST http://localhost:8000/analyze \
298 |   -H "Content-Type: application/json" \
299 |   -d '{"local_path": "/path/to/project"}'
300 | 
301 | # Check status
302 | curl http://localhost:8000/jobs/{job_id}
303 | ```
304 | 
305 | ## Architecture Overview
306 | 
307 | ```
308 | ┌─────────────────────────────────────────┐
309 | │         VSCode Extension                │
310 | │  ┌───────────────────────────────────┐  │
311 | │  │     SidebarProvider.ts            │  │
312 | │  │  - Manages webview UI             │  │
313 | │  │  - Handles user interactions      │  │
314 | │  │  - Polls backend for updates      │  │
315 | │  └───────────────┬───────────────────┘  │
316 | │                  │                       │
317 | │                  │ HTTP Requests         │
318 | │                  ▼                       │
319 | └──────────────────┼───────────────────────┘
320 |                    │
321 |                    │ POST /analyze
322 |                    │ GET /jobs/{id}
323 |                    │
324 | ┌──────────────────▼───────────────────────┐
325 | │         FastAPI Backend                  │
326 | │  ┌───────────────────────────────────┐  │
327 | │  │         main.py                   │  │
328 | │  │  - API endpoints                  │  │
329 | │  │  - Job management                 │  │
330 | │  │  - CORS handling                  │  │
331 | │  └───────────────┬───────────────────┘  │
332 | │                  │                       │
333 | │                  ▼                       │
334 | │  ┌───────────────────────────────────┐  │
335 | │  │      orchestrate.py               │  │
336 | │  │  - Coordinates analysis pipeline  │  │
337 | │  │  - Updates progress               │  │
338 | │  └───────────────┬───────────────────┘  │
339 | │                  │                       │
340 | │                  ▼                       │
341 | │  ┌───────────────────────────────────┐  │
342 | │  │      WatsonX AI Agent             │  │
343 | │  │  - Analyzes code                  │  │
344 | │  │  - Generates insights             │  │
345 | │  └───────────────────────────────────┘  │
346 | └──────────────────────────────────────────┘
347 | ```
348 | 
349 | ## Next Steps
350 | 
351 | 1. **Enhance UI**: Add tabs for different analysis sections
352 | 2. **Add Commands**: Register VSCode commands for quick actions
353 | 3. **Settings**: Add VSCode settings for backend URL configuration
354 | 4. **Notifications**: Show VSCode notifications for analysis completion
355 | 5. **Results View**: Create dedicated views for detailed results
356 | 
357 | ## Support
358 | 
359 | For issues or questions:
360 | 1. Check the backend logs
361 | 2. Check VSCode DevTools console
362 | 3. Review this setup guide
363 | 4. Check the main README.md
364 | 
365 | ---
366 | 
367 | Made with Bob

</file_content>

<file_content path="vscode-extension/tsconfig.json">
 1 | {
 2 |   "compilerOptions": {
 3 |     "module": "commonjs",
 4 |     "target": "ES2020",
 5 |     "outDir": "out",
 6 |     "lib": [
 7 |       "ES2020",
 8 |       "DOM"
 9 |     ],
10 |     "sourceMap": true,
11 |     "rootDir": "src",
12 |     "strict": true,
13 |     "esModuleInterop": true,
14 |     "skipLibCheck": true,
15 |     "typeRoots": ["./node_modules/@types"],
16 |     "forceConsistentCasingInFileNames": true,
17 |     "resolveJsonModule": true
18 |   },
19 |   "exclude": [
20 |     "node_modules",
21 |     ".vscode-test"
22 |   ]
23 | }
24 | 
25 | // Made with Bob

</file_content>
</file_content>
<environment_details>
# VSCode Visible Files
vscode-extension\SETUP.md

# VSCode Open Tabs
vscode-extension/SETUP.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:48:56.500Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>


# Current Workspace Directory (c:/Users/SOORYA/OneDrive/Documents/Extra Curriculars/Hackathons/IBM Bob) Files
.bob
.env.example
.gitignore
package-lock.json
package.json
README.md
backend/
backend/.pylintrc
backend/pyproject.toml
backend/pytest.ini
backend/requirements-dev.txt
backend/requirements.txt
backend/setup.py
backend/src/
backend/src/__init__.py
backend/src/config.py
backend/src/jobs.py
backend/src/main.py
backend/src/models.py
backend/src/orchestrate_client.py
backend/src/orchestrate.py
backend/src/parser.py
backend/src/watsonx.py
backend/src/utils/
backend/src/utils/__init__.py
backend/src/utils/logger.py
backend/tests/
backend/tests/__init__.py
backend/tests/conftest.py
backend/tests/integration_test.py
backend/tests/test_config.py
backend/tests/test_jobs.py
backend/tests/test_logger.py
backend/tests/test_main.py
backend/tests/test_models.py
backend/tests/test_orchestrate.py
backend/tests/test_parser.py
backend/tests/Tests.md
backend/tests/fixtures/
backend/tests/fixtures/sample_repos/
bob_sessions/
documentation/
documentation/agent-configurations.md
documentation/filetree.md
documentation/orchestrate-integration.md
documentation/teamspec.md
vscode-extension/
vscode-extension/.gitignore
vscode-extension/package-lock.json
vscode-extension/package.json
vscode-extension/README.md
vscode-extension/SETUP.md
vscode-extension/tsconfig.json
vscode-extension/media/
vscode-extension/media/icon.svg
vscode-extension/src/
vscode-extension/src/config.ts
vscode-extension/src/extension.ts
vscode-extension/src/SidebarProvider.ts
vscode-extension/webview/
vscode-extension/webview/ARCHITECTURE_ISSUES.md
vscode-extension/webview/COMPLETE_GUIDE.md
vscode-extension/webview/db_schema.md
vscode-extension/webview/DEPENDENCY_TREE_IMPLEMENTATION.md
vscode-extension/webview/graph_spec.md
vscode-extension/webview/main.html
vscode-extension/webview/main.js
vscode-extension/webview/P4_P5_INTEGRATION_GUIDE.md
vscode-extension/webview/README.md
vscode-extension/webview/sample-data-complex.js
vscode-extension/webview/sample-data.js
vscode-extension/webview/styles.css
vscode-extension/webview/test-complex-tree.html
vscode-extension/webview/test-dependency-tree.html
vscode-extension/webview/TESTING_GUIDE.md
vscode-extension/webview/TODO
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you understand how to install the VSCode extension. Let me read the relevant documentation files to provide you with complete installation instructions.

<read_file>
<path>vscode-extension/README.md</path>
</read_file>

<read_file>
<path>vscode-extension/SETUP.md</path>
</read_file>

Based on the documentation, here are the installation methods for the RepoSense VSCode extension:

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'vscode-extension/README.md'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
The tool execution failed with the following error:
<error>
Tool "read_file" is not allowed in orchestrator mode.
</error>
Tool [read_file] was not executed because a tool has already been used in this message. Only one tool may be used per message. You must assess the first tool's result before proceeding to use the next tool.
<environment_details>
# VSCode Visible Files
vscode-extension\SETUP.md

# VSCode Open Tabs
vscode-extension/SETUP.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:49:02.457Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Based on the file contents you've provided, here are the **two main ways to install the VSCode extension**:

## **Method 1: Install from Source (Development)**

1. **Navigate to the extension directory:**
   ```bash
   cd vscode-extension
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Compile the extension:**
   ```bash
   npm run compile
   ```

4. **Run in development mode:**
   - Open the [`vscode-extension`](vscode-extension) folder in VSCode
   - Press `F5` to open a new VSCode window with the extension loaded

## **Method 2: Install from VSIX Package**

1. **Package the extension** (if not already packaged):
   ```bash
   cd vscode-extension
   npm install -g @vscode/vsce
   vsce package
   ```
   This creates a `.vsix` file.

2. **Install the VSIX:**
   - Open VSCode
   - Go to Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`)
   - Click the `...` menu at the top
   - Select "Install from VSIX..."
   - Choose the `.vsix` file

## **Prerequisites**

Before installation, ensure you have:
- **Node.js** version 16.x or higher
- **VSCode** version 1.74.0 or higher
- **Backend service** running on `http://localhost:8000`

## **Post-Installation**

After installing, you'll need to:
1. Start the RepoSense backend service
2. Click the RepoSense icon in the Activity Bar (left sidebar)
3. Open a workspace/folder in VSCode
4. Click "Analyze Workspace" to use the extension

The extension is configured in [`package.json`](vscode-extension/package.json:1) and compiled using TypeScript settings from [`tsconfig.json`](vscode-extension/tsconfig.json:1).

---

**User:**

[ERROR] You did not use a tool in your previous response! Please retry with a tool use.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name itself becomes the XML tag name. Each parameter is enclosed within its own set of tags. Here's the structure:

<actual_tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</actual_tool_name>

For example, to use the attempt_completion tool:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always use the actual tool name as the XML tag name for proper parsing and execution.

# Next Steps

If you have completed the user's task, use the attempt_completion tool.
If you require additional information from the user, use the ask_followup_question tool.
Otherwise, if you have not completed the task and do not need additional information, then proceed with the next step of the task.
(This is an automated message, so do not respond to it conversationally.)
<environment_details>
# VSCode Visible Files
vscode-extension\SETUP.md

# VSCode Open Tabs
vscode-extension/SETUP.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:49:12.251Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.09

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Based on the documentation files provided, here are the two installation methods for the VSCode extension:

## Method 1: Install from Source (Development)
1. Navigate to extension directory: `cd vscode-extension`
2. Install dependencies: `npm install`
3. Compile the extension: `npm run compile`
4. Press `F5` in VSCode to open a new window with the extension loaded

## Method 2: Install from VSIX Package
1. Download or create the `.vsix` file (using `vsce package`)
2. Open VSCode Extensions view (`Ctrl+Shift+X`)
3. Click `...` menu → "Install from VSIX..."
4. Select the `.vsix` file

## Prerequisites
- Node.js 16.x or higher
- VSCode 1.74.0 or higher
- Backend service running on `http://localhost:8000`

Full setup instructions are documented in [`SETUP.md`](vscode-extension/SETUP.md:1) and [`README.md`](vscode-extension/README.md:1).
</result>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
how does pressing f5 know to run extension when the extension is not the
</feedback>
<environment_details>
# VSCode Visible Files
vscode-extension\SETUP.md

# VSCode Open Tabs
vscode-extension/SETUP.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:50:30.325Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.18

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<ask_followup_question>
<question>I understand your question - you're asking how pressing F5 knows to run the extension. This works through VSCode's launch configuration. Let me check if there's a `.vscode/launch.json` file that configures this. Would you like me to:</question>
<follow_up>
<suggest>Check for the .vscode/launch.json configuration file that tells VSCode how to run the extension when F5 is pressed</suggest>
<suggest>Explain that you need to open the vscode-extension folder specifically in VSCode (not the root project folder) for F5 to work</suggest>
<suggest>Show you how to manually create the launch.json file if it's missing</suggest>
<suggest>Provide alternative installation methods that don't require F5 debugging</suggest>
</follow_up>
</ask_followup_question>

---

**User:**

[ask_followup_question for 'I understand your question - you're asking how pressing F5 knows to run the extension. This works through VSCode's launch configuration. Let me check if there's a `.vscode/launch.json` file that configures this. Would you like me to:'] Result:
<answer>
ok, launch it
</answer>
<environment_details>
# VSCode Visible Files
.vscode\launch.json

# VSCode Open Tabs
vscode-extension/.vscode/launch.json,.vscode/launch.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:52:54.414Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.28

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<new_task>
<mode>ask</mode>
<message>I can see there are two `.vscode/launch.json` files open in the tabs. I need to examine the launch configuration in the `vscode-extension/.vscode/` directory to explain how F5 knows to run the extension.

Please read the file at `vscode-extension/.vscode/launch.json` and explain:
1. How the launch configuration works
2. What happens when you press F5
3. Why you need to open the vscode-extension folder specifically in VSCode for this to work
4. What the configuration does to launch the extension in debug mode

If the file doesn't exist, explain that it needs to be created and provide the standard VSCode extension launch configuration.</message>
</new_task>

---

**User:**

[new_task completed] Result: # VSCode Extension Launch Configuration Explained

## How the Launch Configuration Works

The [`launch.json`](vscode-extension/.vscode/launch.json:1) file defines debug configurations for VSCode. Here's what each part does:

### Configuration Breakdown

1. **`"type": "extensionHost"`** (line 6)
   - This is the critical setting that tells VSCode this is an **extension development** configuration
   - It launches a special "Extension Development Host" - a new VSCode window that runs your extension

2. **`"request": "launch"`** (line 7)
   - Starts a new debug session (as opposed to "attach" which connects to an existing process)

3. **`"args": ["--extensionDevelopmentPath=${workspaceFolder}"]`** (lines 8-10)
   - Passes the current workspace folder as the extension development path
   - `${workspaceFolder}` resolves to `vscode-extension/` when that folder is open
   - This tells VSCode where to find the extension code to load

4. **`"outFiles": ["${workspaceFolder}/out/**/*.js"]`** (lines 11-13)
   - Specifies where the compiled JavaScript files are located
   - Enables source map support for debugging TypeScript code
   - The debugger uses these to map breakpoints from `.ts` files to the compiled `.js` files

5. **`"preLaunchTask": "${defaultBuildTask}"`** (line 14)
   - Automatically compiles the TypeScript code before launching
   - Runs the default build task (typically `npm run compile` or `tsc`)
   - Ensures you're always debugging the latest code

## What Happens When You Press F5

Here's the sequence of events:

```mermaid
sequenceDiagram
    participant User
    participant VSCode
    participant BuildTask
    participant ExtHost as Extension Host
    participant Extension

    User->>VSCode: Press F5
    VSCode->>BuildTask: Run preLaunchTask (compile TypeScript)
    BuildTask->>BuildTask: tsc compiles .ts → .js files
    BuildTask-->>VSCode: Build complete
    VSCode->>ExtHost: Launch new VSCode window
    ExtHost->>Extension: Load extension from workspaceFolder
    Extension->>ExtHost: Activate extension
    ExtHost-->>User: Extension Development Host ready
    Note over User,ExtHost: Debug session active with breakpoints
```

1. **Build Phase**: TypeScript files are compiled to JavaScript in the `out/` directory
2. **Launch Phase**: A new VSCode window opens (the Extension Development Host)
3. **Load Phase**: Your extension is loaded from the compiled files
4. **Activation Phase**: The extension's [`activate()`](vscode-extension/src/extension.ts:1) function is called
5. **Debug Phase**: You can now set breakpoints, inspect variables, and debug your extension

## Why You Need to Open `vscode-extension/` Specifically

This is crucial for three reasons:

### 1. **`${workspaceFolder}` Resolution**
   - When you open `vscode-extension/` as the workspace root, `${workspaceFolder}` resolves to that directory
   - If you opened the parent directory (`IBM Bob/`), `${workspaceFolder}` would point to the wrong location
   - The extension host wouldn't find your extension code

### 2. **`.vscode/` Directory Scope**
   - VSCode only reads `.vscode/launch.json` from the **root** of the opened workspace
   - If you open `IBM Bob/`, VSCode reads `.vscode/launch.json` from there (which has different configurations)
   - The `vscode-extension/.vscode/launch.json` would be ignored

### 3. **Relative Path Resolution**
   - The `outFiles` path `${workspaceFolder}/out/**/*.js` expects `out/` to be at the workspace root
   - Build tasks and file watchers also rely on being at the correct root directory

### Visual Example

```
❌ Wrong: Opening IBM Bob/
IBM Bob/                          ← workspaceFolder points here
├── .vscode/
│   └── launch.json              ← This one is used (wrong config)
└── vscode-extension/
    ├── .vscode/
    │   └── launch.json          ← This one is ignored
    └── out/                      ← Can't find this (wrong path)

✅ Correct: Opening vscode-extension/
vscode-extension/                 ← workspaceFolder points here
├── .vscode/
│   └── launch.json              ← This one is used (correct!)
├── out/                          ← Found at ${workspaceFolder}/out/
└── src/
    └── extension.ts
```

## What the Configuration Does in Debug Mode

When you press F5, the configuration:

1. **Compiles your code** - Ensures latest changes are built
2. **Launches a sandboxed VSCode instance** - Isolated from your main VSCode
3. **Loads your extension** - As if it were installed from the marketplace
4. **Enables debugging features**:
   - Set breakpoints in TypeScript source files
   - Step through code execution
   - Inspect variables and call stacks
   - View console output in the Debug Console
   - Hot reload on code changes (with watch mode)

5. **Provides a test environment** - The Extension Development Host acts as a real VSCode instance where you can test your extension's functionality

## Summary

The [`launch.json`](vscode-extension/.vscode/launch.json:1) configuration is specifically designed for VSCode extension development. It automates the build-launch-debug cycle and requires opening the `vscode-extension/` folder as the workspace root so that all paths resolve correctly and VSCode can find the extension code to load into the Extension Development Host.

---

**User:**

[new_task in ❓ Ask mode: 'I can see there are two `.vscode/launch.json` files open in the tabs. I need to examine the launch configuration in the `vscode-extension/.vscode/` directory to explain how F5 knows to run the extension.

Please read the file at `vscode-extension/.vscode/launch.json` and explain:
1. How the launch configuration works
2. What happens when you press F5
3. Why you need to open the vscode-extension folder specifically in VSCode for this to work
4. What the configuration does to launch the extension in debug mode

If the file doesn't exist, explain that it needs to be created and provide the standard VSCode extension launch configuration.'] Result:
Successfully created new task in ❓ Ask mode with message: I can see there are two `.vscode/launch.json` files open in the tabs. I need to examine the launch configuration in the `vscode-extension/.vscode/` directory to explain how F5 knows to run the extension.

Please read the file at `vscode-extension/.vscode/launch.json` and explain:
1. How the launch configuration works
2. What happens when you press F5
3. Why you need to open the vscode-extension folder specifically in VSCode for this to work
4. What the configuration does to launch the extension in debug mode

If the file doesn't exist, explain that it needs to be created and provide the standard VSCode extension launch configuration. and 0 todo items
[new_task in ❓ Ask mode: 'I can see there are two `.vscode/launch.json` files open in the tabs. I need to examine the launch configuration in the `vscode-extension/.vscode/` directory to explain how F5 knows to run the extension.

Please read the file at `vscode-extension/.vscode/launch.json` and explain:
1. How the launch configuration works
2. What happens when you press F5
3. Why you need to open the vscode-extension folder specifically in VSCode for this to work
4. What the configuration does to launch the extension in debug mode

If the file doesn't exist, explain that it needs to be created and provide the standard VSCode extension launch configuration.'] Result:
Successfully created new task in ❓ Ask mode with message: I can see there are two `.vscode/launch.json` files open in the tabs. I need to examine the launch configuration in the `vscode-extension/.vscode/` directory to explain how F5 knows to run the extension.

Please read the file at `vscode-extension/.vscode/launch.json` and explain:
1. How the launch configuration works
2. What happens when you press F5
3. Why you need to open the vscode-extension folder specifically in VSCode for this to work
4. What the configuration does to launch the extension in debug mode

If the file doesn't exist, explain that it needs to be created and provide the standard VSCode extension launch configuration. and 0 todo items
<environment_details>
# VSCode Visible Files
.vscode\launch.json

# VSCode Open Tabs
vscode-extension/.vscode/launch.json,.vscode/launch.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:53:41.529Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.37

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
## How F5 Knows to Run the Extension

The [`vscode-extension/.vscode/launch.json`](vscode-extension/.vscode/launch.json:1) file contains a debug configuration that tells VSCode how to run the extension when you press F5.

### Key Configuration Settings

1. **`"type": "extensionHost"`** - Tells VSCode this is an extension development configuration
2. **`"args": ["--extensionDevelopmentPath=${workspaceFolder}"]`** - Points to where the extension code is located
3. **`"outFiles": ["${workspaceFolder}/out/**/*.js"]`** - Specifies the compiled JavaScript files
4. **`"preLaunchTask": "${defaultBuildTask}"`** - Compiles TypeScript before launching

### What Happens When You Press F5

1. TypeScript files are compiled to JavaScript (`npm run compile`)
2. A new VSCode window opens (Extension Development Host)
3. Your extension is loaded from the compiled files
4. The extension's `activate()` function is called
5. You can now debug with breakpoints and inspect variables

### Why You Must Open `vscode-extension/` Folder

**Critical**: You must open the `vscode-extension/` folder specifically in VSCode, not the parent `IBM Bob/` folder.

- `${workspaceFolder}` resolves to the opened folder's root
- If you open `IBM Bob/`, VSCode reads the wrong `.vscode/launch.json`
- The paths to `out/` and extension files won't resolve correctly

### Correct Installation Steps

1. Open **only** the `vscode-extension/` folder in VSCode
2. Run `npm install` and `npm run compile`
3. Press `F5` to launch the Extension Development Host
4. Test your extension in the new window
</result>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
change current launch.json to enable me to launch from main workspace.
</feedback>
<environment_details>
# VSCode Visible Files
.vscode\launch.json

# VSCode Open Tabs
vscode-extension/.vscode/launch.json,.vscode/launch.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:55:35.257Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.48

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<new_task>
<mode>code</mode>
<message>I need to modify the root `.vscode/launch.json` file to add a configuration that allows launching the VSCode extension from the main workspace (IBM Bob/).

The task is to:
1. Read the current `.vscode/launch.json` file at the root
2. Add a new launch configuration for the VSCode extension that:
   - Has `"type": "extensionHost"`
   - Points to `${workspaceFolder}/vscode-extension` as the extension development path
   - Uses `${workspaceFolder}/vscode-extension/out/**/*.js` for outFiles
   - Includes a preLaunchTask to compile the extension
   - Has a clear name like "Run VSCode Extension"
3. Preserve any existing configurations in the file
4. Ensure the JSON is properly formatted

This will allow the user to press F5 from the main workspace and launch the extension without having to open the vscode-extension folder separately.</message>
</new_task>

---

**User:**

[new_task completed] Result: Successfully modified the root `.vscode/launch.json` file to add a proper configuration for launching the VSCode extension from the main workspace. 

Changes made:
1. ✅ Updated the configuration name to "Run VSCode Extension" for clarity
2. ✅ Fixed the `--extensionDevelopmentPath` to point to `${workspaceFolder}/vscode-extension` (was incorrectly pointing to just `${workspaceFolder}`)
3. ✅ Kept the correct `outFiles` path: `${workspaceFolder}/vscode-extension/out/**/*.js`
4. ✅ Updated the `preLaunchTask` to `npm: compile - vscode-extension` to properly compile the extension before launching
5. ✅ Maintained proper JSON formatting

You can now press F5 from the main workspace (IBM Bob/) to launch the VSCode extension without having to open the vscode-extension folder separately. The extension will be compiled automatically before launching.

---

**User:**

[new_task in 💻 Code mode: 'I need to modify the root `.vscode/launch.json` file to add a configuration that allows launching the VSCode extension from the main workspace (IBM Bob/).

The task is to:
1. Read the current `.vscode/launch.json` file at the root
2. Add a new launch configuration for the VSCode extension that:
   - Has `"type": "extensionHost"`
   - Points to `${workspaceFolder}/vscode-extension` as the extension development path
   - Uses `${workspaceFolder}/vscode-extension/out/**/*.js` for outFiles
   - Includes a preLaunchTask to compile the extension
   - Has a clear name like "Run VSCode Extension"
3. Preserve any existing configurations in the file
4. Ensure the JSON is properly formatted

This will allow the user to press F5 from the main workspace and launch the extension without having to open the vscode-extension folder separately.'] Result:
Successfully created new task in 💻 Code mode with message: I need to modify the root `.vscode/launch.json` file to add a configuration that allows launching the VSCode extension from the main workspace (IBM Bob/).

The task is to:
1. Read the current `.vscode/launch.json` file at the root
2. Add a new launch configuration for the VSCode extension that:
   - Has `"type": "extensionHost"`
   - Points to `${workspaceFolder}/vscode-extension` as the extension development path
   - Uses `${workspaceFolder}/vscode-extension/out/**/*.js` for outFiles
   - Includes a preLaunchTask to compile the extension
   - Has a clear name like "Run VSCode Extension"
3. Preserve any existing configurations in the file
4. Ensure the JSON is properly formatted

This will allow the user to press F5 from the main workspace and launch the extension without having to open the vscode-extension folder separately. and 0 todo items
[new_task in 💻 Code mode: 'I need to modify the root `.vscode/launch.json` file to add a configuration that allows launching the VSCode extension from the main workspace (IBM Bob/).

The task is to:
1. Read the current `.vscode/launch.json` file at the root
2. Add a new launch configuration for the VSCode extension that:
   - Has `"type": "extensionHost"`
   - Points to `${workspaceFolder}/vscode-extension` as the extension development path
   - Uses `${workspaceFolder}/vscode-extension/out/**/*.js` for outFiles
   - Includes a preLaunchTask to compile the extension
   - Has a clear name like "Run VSCode Extension"
3. Preserve any existing configurations in the file
4. Ensure the JSON is properly formatted

This will allow the user to press F5 from the main workspace and launch the extension without having to open the vscode-extension folder separately.'] Result:
Successfully created new task in 💻 Code mode with message: I need to modify the root `.vscode/launch.json` file to add a configuration that allows launching the VSCode extension from the main workspace (IBM Bob/).

The task is to:
1. Read the current `.vscode/launch.json` file at the root
2. Add a new launch configuration for the VSCode extension that:
   - Has `"type": "extensionHost"`
   - Points to `${workspaceFolder}/vscode-extension` as the extension development path
   - Uses `${workspaceFolder}/vscode-extension/out/**/*.js` for outFiles
   - Includes a preLaunchTask to compile the extension
   - Has a clear name like "Run VSCode Extension"
3. Preserve any existing configurations in the file
4. Ensure the JSON is properly formatted

This will allow the user to press F5 from the main workspace and launch the extension without having to open the vscode-extension folder separately. and 0 todo items
<environment_details>
# VSCode Visible Files
.vscode\launch.json

# VSCode Open Tabs
.vscode/launch.json

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T07:56:40.178Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.58

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**
- bob_sessions/

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Successfully updated [`.vscode/launch.json`](.vscode/launch.json:1) to enable launching the VSCode extension from the main workspace.

## Changes Made

The root launch configuration now includes:
- **Name**: "Run VSCode Extension" for easy identification
- **Extension Path**: Points to `${workspaceFolder}/vscode-extension`
- **Output Files**: Correctly references `${workspaceFolder}/vscode-extension/out/**/*.js`
- **Pre-Launch Task**: Compiles the extension before launching

## How to Use

1. Ensure you're in the main workspace (IBM Bob/)
2. Run `npm install` in the `vscode-extension/` directory (first time only)
3. Press `F5` or select "Run VSCode Extension" from the debug dropdown
4. The extension will compile automatically and launch in a new VSCode window

You can now develop and debug the extension without switching workspace folders.
</result>
</attempt_completion>

