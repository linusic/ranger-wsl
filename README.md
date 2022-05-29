# ranger-wsl
The content of this repository is about the configuration,scripts and custom commands of `Ranger` in the `WSL` environment 

- 🚀[Ranger](https://github.com/ranger/ranger)
- 🚀[WSL](https://github.com/microsoft/WSL)

You can run WindowsOS Applications in your WSL-Ranger
- 🎉`editor`: use your windows [sublime text](https://www.sublimetext.com/) / `notepad.exe` as your default editor for `Ranger`
- 🎉`player`: use your windows browser to open Audio/Video/PDF (or use others app VLC ...)
- 🎉`compress/extract`: I just provide `Rar.exe/unRar.exe` code for `WinRar.exe`
- ...
- If WindowsOS App provides a command line to start, then you can integrate them into WSL-Ranger

## Instructions
my `WSL` path format is default, so the `prefix` is :👇
```shell
/mnt/

# eg:
# /mnt/c
# /mnt/d
# /mnt/e
# ...

```

all my scripts follow above path format `prefix`👆  
> 🔥If you had changed your default location of `WSL` , eg: not `/mnt/`  
> 🔥you need to change these scripts by yourself, replace to your own path format  
> 🚀`Python3.6+`

## Core Script
- `ri_script/wsl_2_path.py` 
- `ri_script/wsl_2_url.py`

> the contents of scripts are very simple.  
> but the main idea is: `Which applications` need to be converted to `which path format`.  

eg: you can run `chrome.exe` to open `Video/Audio/PDF` and more files  
- but you cant't open them with absolute path  
- you must switch: `/mnt/{}/xxx` to `file:///{}:/xxx`
- for details, you can try: `ri_script/wsl_2_url.py`


## commands.py 
- bulkrename: change editor in `rc.conf` =>  `mime ^text, label editor =`
  - changed: default editor is `subl.exe`  you can set your editor 👆

- fzf_select
  - refer from [ranger-wiki](https://github.com/ranger/ranger/wiki/Custom-Commands#fzf-integration): 
  - changed: some code and add my fzf remap/config

- fzf_mark
  - I add the fzf_mark, you can also see [fzf_mark](https://github.com/ranger/ranger/wiki/Custom-Commands#fzf-filter-and-mark)

- extract_here & compress
  - refer from [archlinux-wiki](https://wiki.archlinux.org/title/Ranger#Compression)
  - changed: replace `atool` in ArchLinux to `WinRAR.exe` in Windows for WSL

## rifle.conf
you can see  the type of files name `suffix` and associated WindowsOS Applications

## rc.conf
you can see above 👆 `commands.py` remap in `rc.conf`
> end of `rc.conf` =>  `source ~/rc_remap.conf` is for AutoWalk 👇

## [AutoWalk](https://github.com/linusic/autowalk)
you can AutoWalk to bulk add remap for Ranger for paths in your filesystem 


## Others
### JupyterLab For Ranger
In ranger, you can open `.ipynb` on JupyterLab directly;  
But it depends on [PM2](https://github.com/Unitech/pm2); 
add below in your `rifle.conf`: 
```shell
ext ipynb  = python3 ~/ri_script/jlab_ranger.py $1
```
> Note: you need to adjust the paths of the script: `ri_script/jlab_ranger.py` to your `home_dir`

### Launch WSL Application on Windows directly
Maybe some configure didn't work with `wsl.exe  --exec`,  you can try 👇

put source application configure into `/etc/profile`
> Q: Why `/etc/profile` rather than `~/.zshrc` ?  
> A: Decoupling makes `bash` faster than `zsh` for launching (Ranger just needs `fzf configure`)

```shell
echo '[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh' >> /etc/profile
```
then put below code into your windows app manager (Lnk ...)
```shell
wsl.exe  --exec /bin/zsh -c "source /etc/profile && ranger /mnt/d/test"
```
