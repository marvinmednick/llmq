Project Setup:
Uses template for python-version with the following filters:
git config filter.templated-file.clean "cat /path/to/template/file"
git config filter.templated-file.smudge "cat"

and has .python-version defined in .gitattributes
