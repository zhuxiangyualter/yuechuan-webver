

<div align="center">
 <img alt="LOGO" src="https://s2.loli.net/2024/04/15/T698o4cpuUmeSyW.png" width="100" height="100" />
 <h3>AILearn</h3>
 An integrated learning platform designed for student-teacher and student-student collaboration, enhanced by Artificial Intelligence utilities. 
</div>

---

## Prerequisties

The following items are required for this project:  
- [Python](https://python.org) **v3.12+**.
- [Poetry](https://python-poetry.org).
- An [OpenAI](https://openai.com) API key.
- A [Xunfei](https://www.xfyun.cn/) API key.

## Deploy

Clone this repo:

```sh
$ git clone https://github.com/aurora-wangq/AILearn.git
```

Create a virtual environment and install dependencies:

```sh
$ poetry install
```

Spawn virtual environment shell:

```sh
$ poetry shell
```

Edit environment variables:  

```sh
$ cp .env.template .env
$ vim .env # or whichever editor you like
```

Migrate database:

```sh
$ py manage.py migrate
```

Run server:

```sh
$ py manage.py runserver
```

Visit http://localhost:8000

## Contributor
<div>
<a href="https://github.com/MoveToEx">
    <img src="https://avatars.githubusercontent.com/u/39954725?v=4" height=50px; width=50px;>
</a>
<a href="https://github.com/aurora-wangq">
    <img src="https://avatars.githubusercontent.com/u/54229986?v=4" height=50px; width=50px;>
</a>
</div>


