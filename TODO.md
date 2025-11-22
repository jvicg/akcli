# ToDo 

> Development roadmap for `akcli`.

## General
- [ ] Create TypedDict por TableParams and ColumnsHeaders (?) [P3] [feature] 
- [ ] Generate Pydantic models automatically (See: https://github.com/koxudaxi/datamodel-code-generator) [P2] [feature]
- [ ] Log errors and warnings using `logging` (?) [P2] [logs]
- [ ] Create command to make requests to customs API endpoints (E.g: `akcli custom /api/v1/custom/endpoint/`) [P2] [feature]
- [x] Consider if `api` public methods should return Pydantic models (?) [P2] [refactor]
- [x] Find a way to create tables dinamically on `dig` and `translate` based on API response [P2] [refactor] [investigate]
- [x] Move `handle_exception()` ouf of `utils.py`
- [x] Move `utils.parsing` to another module [P2] [refactor]
- [x] Create type aliases module [P3] [refactor]
- [x] Move constants to independent module [refactor] [investigate] (Solved moving them to `config.py`)
- [x] Add support for config file [P1] [feature]
- [x] Add cache support (See: https://grantjenks.com/docs/diskcache/) [P1] [feature]
- [x] Create submodules of utils.py [refactor]
- [x] Improve stdout using `rich` [P3] [ui]
- [x] Improve exceptions [refactor]

---

## Docs
- [ ] Create documentation using Sphinx [P1] [docs]
- [x] Improve docstrings and general code documentation [P3] [docs]

---

## Testing
- [ ] Implement tests [P1] [tests]

---

## Modules

### main.py
- [ ] Consider if refactor `--init-config-file` as a subcommand (?) [P3] [refactor]
- [ ] Refactor `main.py` declaration to be more legible (See: https://chatgpt.com/g/g-p-68e93e2f10248191836d4a86771a114e/c/68f39dfe-6a3c-8331-9738-651a3caed55a) [P2] [refactor]
- [ ] Check if autocompletions works
- [ ] Add flags [P2] [feature]
    - [ ] to output result into csv format [P2] [feature]
    - [ ] to disable warning messages [P2] [feature]
    - [ ] for verbose option  (See: https://rich.readthedocs.io/en/stable/logging.html) (?) [P3] [cli]
    - [x] to output result into json format [P2] [feature]
    - [x] for custom `.edgerc` section [P2] [feature]
    - [x] for proxy [feature]
    - [x] for custom requests timeout [feature]
    - [x] for custom validate certs input [feature]
- [x] Improve help panel [P2] [ui]
- [x] Handle malformed proxies [P2] [error-handling]

---

### cache.py
- [ ] Handle errors in scenarios when is not possible to save/load cache file [P2] [error-handling]
- [x] Check if expires_at logic really has to be inside of `_CacheItem` [P2] [refactor]
- [x] Double check `_CacheItem.to_dict()` since is loses `_CacheItem.key` [P2] [refactor]

---

### config.py
- [ ] Find a clean way to don't print warnings in `config.py`. i.e: Raise exception a capture in `main.py` [P2] [refactor]
- [ ] Create a flag to save the selected options in to the config file [P2] [feature]
- [ ] Ask for confirmation if config file exists on `init_config_file()`[P2] [feature]
- [ ] Add support for a custom file path [P3] [feature]
- [x] Prevent user to set config parameters that doesn't exist [P1] [fix]
- [x] Find a way to don't need to initialize a Console instance on `init_config_file()` [P2] [refactor]

---

### exceptions.py
- [x] Classify error codes by type of error [P3] [refactor] [error-handling]

---

### commands/translate.py
- [ ] Handle also scenarios when `obj` is a list `_add_subtable()` [P2] [refactor]
- [ ] Check the different errors it can return [P2] [feature]
- [x] Create configuration file section for this command [P1] [feature]
- [x] Create the table [P1] [feature]
- [x] Create Pydantic models [P2] [feature]

---

### commands/dig.py
- [ ] Add flags [P2] [cli]
    - [ ] for raw dig output [P2] [feature]
    - [x] for short mode [P3] [feature]

---

### ️ api.py
- [x] Create `_build_base_headers()` method [P3] [feature] 
- [x] Handle errors when `.edgerc` is malformed [P2] [error-handling]
- [x] Improve `_requests()` exceptions [P1] [refactor]
- [x] Centralize all requests logic into `api.py` [P1] [refactor]

---

### models/
- [ ] Models need a general improvement and a double check [P2] [refactor] [test]
- [ ] Create `errors.py`. See API errors response: (https://techdocs.akamai.com/edge-diagnostics/reference/dig) [P2] [models]

---

### utils.py
- [x] Refactor `parse_response()` to be more reusable [P2] [refactor]
- [x] Create `create_panel()` function [P2] [ui]
- [x] Make `create_table()` more reusable [ui]
