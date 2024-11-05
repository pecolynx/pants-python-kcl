poetry_requirements(
    name="poetry",
)

python_sources(
    name="kcl-app",
    sources=["kcl_app/**/*.py"],
    dependencies=[":poetry"],
)

files(
    name="kcl-app-files",
    sources=[
        "setup.py",
        "logback.xml",
        "pom.xml",
        "run.sh",
        "pyproject.toml",
        "poetry.lock",
        "app.properties",
        "kcl_app/**/*.py"
    ],
)

docker_image(
    name="docker",
    source="Dockerfile",
    dependencies=[":kcl-app-files"],
    context_root="src/python/kcl-app",
    image_tags=["{build_args.GIT_COMMIT_SHA}"]
)
