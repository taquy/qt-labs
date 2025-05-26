
# Using fixed chrome session

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir="$HOME/ChromeProfiles/selenium" \
  --profile-directory="Default"
```
- The path to the profile is $HOME/ChromeProfiles/selenium which will be later used by the script to reusing the same session