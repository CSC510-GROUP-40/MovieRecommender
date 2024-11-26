## Contributing

[fork]: https://github.com/CSC510-GROUP-40/MovieRecommenderfork
[pr]: https://github.com/ebanigogia/MovieRecommender/compare
[style]: https://pep8.org/
[code-of-conduct]: CODE_OF_CONDUCT.md

We're excited that you're interested in contributing to this project! Your support is vital for improving and scaling our **Movie Recommender App**.

If you'd like to contribute and collaborate, please notify us via email at **syepuri@ncsu.edu, chegde@ncsu.edu, or mahamdi@ncsu.edu**.

### Purpose of Contributing

Your contributions help us:
- Develop the product further and take it to the next level.
- Enhance existing features and make the product more efficient.
- Fix critical bugs that users encounter.
- Scale the system to support larger databases.
- Optimize computationally/memory-intensive processes.
- Help the community by delivering a better, more refined product.

### Issues and PRs

If you have ideas for improvements or want to report a bug, open an issue! We'd love to hear your thoughts. For larger contributions, feel free to email us or open an issue first to discuss your proposal.

We also welcome pull requests (PRs). When you submit a PR, one of the repository administrators will review it and merge it after the CI build passes.

### Submitting a Pull Request

1. [Fork][fork] this repository and clone your copy locally.
2. Install the necessary dependencies: `pip install -r requirements.txt`.
3. Make sure the tests pass on your machine: `pytest`.
4. Create a new branch for your feature or fix: `git checkout -b my-branch-name`.
5. Develop your feature, write tests, and ensure everything runs successfully.
6. Push to your fork and [submit a pull request][pr].
7. The repository administrator will review and merge your pull request once it passes the CI build check.

### Code Style and Standards

1. **Style Checkers**: 
   - Use `pylance` in VS Code for Python.
   - Use `black` for auto-styling and formatting the code.
   
2. **Code Style Guidelines**:
   - This project is built using Python (version 3.7). Make sure to add new functionalities in the form of modules.
   - Write self-explanatory variable names and provide comments to help others understand the functionality.
   - Any untested code should be committed under the test folder first. Once successfully tested, the main code can be updated.
   - Follow **PEP 8** guidelines to maintain consistency.
   - `black` is used as a linter for code formatting.

### Code of Conduct

Please take a moment to review the [Code of Conduct][code-of-conduct] before contributing. By contributing, you agree to abide by these guidelines to ensure a positive environment for all contributors.

### Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
- [GitHub Help](https://help.github.com)
