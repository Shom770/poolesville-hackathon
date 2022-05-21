# Our Group's poolesville_hacks Submission
...
## Dev Guide
### Setup
1. First, clone this repository locally with git
2. In the terminal, write `pip install poetry`
3. Run `poetry install` in the terminal to install all dependencies
4. Run `pre-commit install` in the terminal to install the pre-commit hooks.

### Writing Code
Checkout into another branch `git checkout -b [branch name]` and write code from there.
Do **not** write code in the `main` branch and commit there.

Once you write your code out, simply run `git commit -m "your commit message"`, and if it says that there are untracked files, run `git add .` to make all files tracked.
The pre-commit hooks will check what's wrong about the style of your code and the like; black will format your code however if it fails to commit you have to fix what's specified.

Then, run `git push origin [your branch name]` to push to your branch and you're done (remember to open a PR for your branch so it can be merged into main).
