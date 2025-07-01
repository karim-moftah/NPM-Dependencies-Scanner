

## *NPM Dependency Confusion Scanner*

This script helps you detect **unregistered or hijackable dependencies** in JavaScript projects by scanning `package.json` files and checking each dependency name against the public npm registry.





### Usage

#### 1. **Run from a Directory Containing Multiple `package.json` Files**

To scan an entire project (recursively) and check all dependencies:

```python
python3 main.py --dir-path /path/to/your/project
```

- This will search for all `package.json` files under the directory.
- It merges and extracts all dependencies and development dependencies.
- Then it checks each package name against `https://registry.npmjs.com/`.



#### 2. **Run with a Single `package.json` File**

To check one specific `package.json` file:

```python
python3 main.py --json-file /path/to/package.json
```

- This skips the directory search and directly reads the provided file.
- Useful if you’ve already isolated the dependency list or you're only interested in one project.



#### 3. **Optional: Adjust the Delay Between Requests**

To avoid triggering rate limits or reduce load, you can adjust the delay between each check:

```python
python3 main.py --dir-path ./project --delay 1.0
```

- Default delay is `0.5` seconds.
- Increase it if you're checking a large number of dependencies or encounter errors.
