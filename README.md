# I wanted to try using Python Reflex for a local school library app. Here's how it turned out.


# About

This app can do a lot (crud users, books, borrow books, integrations with exel and csv, date things, some statistics and so on).I even tried to create a user-friendly gui.

<img width="2463" height="932" alt="pic" src="https://github.com/user-attachments/assets/3048642e-1387-40ce-adfc-6366ed113638" />

With some modifications it can be run on Linux


# install & run
### for windows:

clone repo `git clone https://github.com/o0wo0o/magicka`
<p>run setup.ps1 in consoe</p>
<p>check /app/utils/config/config.ini and put correct values in browserpath and maybe projectroot</p>
<p>then run run.bat</p> 
wait for setup and follow link (localhost:3000). 

### for linux:
clone repo `git clone https://github.com/o0wo0o/magicka`
<p>manually insall poetry and requirements</p>
<p>check /app/utils/config/config.ini and put correct values in browserpath and maybe projectroot. And change seleniumdriver to correct file</p>
<p>use poetry run reflex run --env prod</p>
<p>wait for setup and follow link (localhost:3000).</p>


