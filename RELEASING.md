1.  Update the version number
``` bash
nano shellypython/__init__.py
```

2.  Generate changelog since the last release
``` bash
# gem install github_changelog_generator --pre
# export CHANGELOG_GITHUB_TOKEN=token
github_changelog_generator --user marcogazzola --project shelly-python --since-tag 0.0.2 -o newchanges
```

3.  Copy the changelog block over to CHANGELOG.md.

4.  Commit the changed files
``` bash
git commit -av
```

5.  Tag a release (and add short changelog as a tag commit message)
``` bash
git tag -a 0.1.0b0 -m "version 0.1.0b0"
```

6.  Push to git
``` bash
git push --tags
```

7.  Upload new version to pypi
``` bash
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```

8.  Click the “Draft a new release” button on github, select the new tag
    and copy & paste the changelog into the description.