# lazy-scripts

I like writing self-contained scripts that do things for me. What I *don't* like is manually handling adding the script
to my path, adding a crafted desktop entry, remembering to give sudo privs if applicable, creating a shortcut for it,
and managing scripting language specific quirks per script.

`lazy-scripts` allows you to just throw the script in a folder, run `lazy-scripts`, and it handles all that for you.

### usage

1. Write a script in any language (currently supported: `.sh`, `.zsh`, `.py`).
2. Drop it into the `./scripts` directory.
3. Run `lazy-scripts` to generate necessary files and install your script.

For example, lets say I create a script to run a package update:

```bash
# ./scripts/upgrade.sh
apt update && apt upgrade -y
```

I call this script `upgrade.sh` and drop it in the `./scripts` folder and run `lazy-scripts`.
Now I can call `upgrade` from anywhere to run the script. 

But wait, there's more.

```bash
# name: Upgrade APT
# desktop: true
# notify: Package upgrade is complete
# sudo: true
apt update && apt upgrade -y
```

I've added some pseudo-frontmatter options at the top of the script file and now I get the following additional stuff:

1. `desktop: true` means that a `.desktop` entry file that runs the script will be added to `~/.local/share/applications`. It will have the title provided in `name`.
2. `notify` will send a desktop notification with the indicated contents upon the script's completion (currently using `notify-send`).
3. `sudo` will ensure the script requests elevated privileges if it doesn't already have them.
4. `zshrc` will treat the current zsh file as a new .zshrc to load a fresh instance of zsh into. Just remember to `source ~/.zshrc` if you want to include your default configuration.

These frontmatter blocks need to be valid YAML and at the top of your script file before any code.
Line comments and block comments in your language of choice are all supported, but don't mix and match.

See the [`./examples`](./examples) folder for everything I have seen fit to publish.

### installation

Just clone the directory and run `lazy-scripts.py`:

```bash
git clone https://github.com/KNOXDEV/lazy-scripts
python3 ./scripts/lazy-scripts.py
```

`lazy-scripts` is itself a lazy script, so you only need to run it once manually to bootstrap it
and you can run `lazy-scripts` in your terminal from anywhere. 

### limitations

When I say "self-contained", its a hard requirement. 
Scripts spanning multiple files will most likely not work the way you imagine.

This project is primarily intended for Linux environments but may *incidentally* function on your platform.

### todo?

1. perhaps allow the `notify` field to include different messages for different exit codes.
2. allow specifying requirements for scripts in frontmatter, such as python packages or OS packages.
3. allow specifying keyboard shortcuts in frontmatter
4. add support for `.js`, `.kts`, `.rb`, etc.