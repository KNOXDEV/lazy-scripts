'''
name: Lazy Scripts Install
desktop: true
pause: true
'''

import os
import re
import yaml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOCAL_BIN = os.path.realpath(f'{os.environ["HOME"]}/.local/share/lazy-scripts/bin')
DESKTOP_ENTRY_DIR = os.path.realpath(f'{os.environ["HOME"]}/.local/share/applications')

SH_PAUSE = """
printf 'press ENTER to continue...'
read _
"""

SCRIPT_TYPES = [
	{
		"ext": ".py",
		"line_comment": "#",
		"block_comments": re.compile(r'^\s*?(\'\'\'|""")([\s\S]*?)\1'),
		"stub": "python3 ",
	},
	{
		"ext": ".sh",
		"line_comment": "#",
		"block_comments": None,
		"stub": "",
	},
	{
		"ext": ".zsh",
		"line_comment": "#",
		"block_comments": None,
		"stub": "",
	}
]

SHELLS = {
	"/usr/bin/zsh": (os.path.join(os.environ['HOME'], ".zshrc"), f'export PATH="{LOCAL_BIN}:$PATH"')
}


def get_script_type(script_filename):
	for stype in SCRIPT_TYPES:
		if script_filename.endswith(stype['ext']):
			return stype
	return None

def get_first_comment_lines(script_path, script_type):
	current_block_comment = None
	with open(script_path, 'r') as script_file:
		file_contents = script_file.read()

	# first check for block comments at the start of the file
	if script_type['block_comments'] is not None:
		match = script_type['block_comments'].match(file_contents)
		if match:
			return match.group(2)

	# next, check for line comments
	lines = []
	for line in file_contents.split("\n"):
		# next check for line comments
		comment_index = line.find(script_type['line_comment'])
		if comment_index == -1:
			if len(line.strip()) == 0:
				continue
			else:
				return None if len(lines) == 0 else "\n".join(lines)
		lines.append(line[comment_index:][len(script_type['line_comment']):])

def get_script_frontmatter(script_path, script_type):
	comment_block = get_first_comment_lines(script_path, script_type)
	if comment_block is None:
		return None
	try:
		frontmatter = yaml.safe_load(comment_block)
		if type(frontmatter) is not dict:
			return None
		return frontmatter
	except yaml.YAMLError as exc:
		return None

def init_local_bin():
	os.makedirs(LOCAL_BIN, exist_ok=True)
	init_path, export_string = SHELLS[os.environ['SHELL']]
	with open(os.path.realpath(init_path), 'r+') as init_file:
		if export_string not in init_file.read():
			print(f"adding {LOCAL_BIN} to path in {init_path}")
			init_file.write('\n# lazy-scripts\n')
			init_file.write(export_string)

def clear_local_bin():
	for stub in os.listdir(LOCAL_BIN):
		os.remove(os.path.join(LOCAL_BIN, stub))

def get_notify_stub(stub_name, notification):
	return f"""
if [ -x "$(command -v notify-send)" ]; then
	notify-send "lazy-scripts: {stub_name}" "{notification}"
fi"""

def emit_to_local_bin(script_path, script_type, script_meta):
	stub_name = os.path.splitext(os.path.basename(script_path))[0]
	stub_path = os.path.join(LOCAL_BIN, stub_name)
	with open(stub_path, 'w') as stub_file:
		if script_meta is not None and script_meta.get("sudo", False):
			stub_file.write("sudo ")
		stub_file.write(script_type['stub'])
		stub_file.write(script_path)
		stub_file.write("\n")
		if script_meta is not None and script_meta.get("notify", False):
			stub_file.write(get_notify_stub(stub_name, script_meta["notify"]))
		if script_meta is not None and script_meta.get("pause", False):
			stub_file.write(SH_PAUSE)

	os.chmod(stub_path, 0o744)
	print(f'wrote stub "{stub_name}" => {script_path}')
	return stub_name, stub_path


def get_desktop_entry(stub_name, stub_path, script_meta):
	name = stub_name if script_meta is None else script_meta.get('name', stub_name)
	lines = [
		"[Desktop Entry]",
		"Type=Application",
		"Terminal=true",
		f"Name={name}",
		"Icon=utilities-terminal",
		f"Exec={stub_path}",
		"Categories=Application;"
	]

	return "\n".join(lines)

def clear_desktop_entries():
	for entry in os.listdir(DESKTOP_ENTRY_DIR):
		if entry.startswith("lazy-scripts-"): 
			os.remove(os.path.join(DESKTOP_ENTRY_DIR, entry))

def main():
	init_local_bin()
	clear_local_bin()
	clear_desktop_entries()

	for script_filename in os.listdir(SCRIPT_DIR):
		script_type = get_script_type(script_filename)
		if script_type is None:
			print(f"skipping file {script_filename}, extension not recognized")
			continue

		script_path = os.path.join(SCRIPT_DIR, script_filename)
		os.chmod(script_path, 0o744)

		meta = get_script_frontmatter(script_path, script_type)
		if meta is not None:
			print(f"{script_filename} is using this configuration => {meta}")

		stub_name, stub_path = emit_to_local_bin(script_path, script_type, meta)

		if meta is not None and meta.get('desktop', False):
			entry_contents = get_desktop_entry(stub_name, stub_path, meta)
			entry_filename = os.path.join(DESKTOP_ENTRY_DIR, f"lazy-scripts-{stub_name}.desktop")
			with open(entry_filename, "w") as entry_file:
				entry_file.write(entry_contents)
			print(f'wrote {stub_name} desktop entry => {entry_filename}')

		print('')

if __name__ == '__main__':
	main()