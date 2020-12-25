[![Download](https://api.bintray.com/packages/gaeus/gaeus-conan/grpc%3Agaeus/images/download.svg) ](https://bintray.com/gaeus/gaeus-conan/grpc%3Agaeus/_latestVersion)
[![Build Status Travis](https://travis-ci.org/gaeus/conan-grpc.svg)](https://travis-ci.org/gaeus/conan-grpc)
[![Build Status AppVeyor](https://ci.appveyor.com/api/projects/status/github/gaeus/conan-grpc?svg=true)](https://ci.appveyor.com/project/gaeus/conan-grpc)

## Docker build with `--no-cache`

```bash
export MY_IP=$(ip route get 8.8.8.8 | sed -n '/src/{s/.*src *\([^ ]*\).*/\1/p;q}')
sudo -E docker build \
    --build-arg PKG_NAME=grpc_conan/v1.26.x \
    --build-arg PKG_CHANNEL=conan/stable \
    --build-arg PKG_UPLOAD_NAME=grpc_conan/v1.26.x@conan/stable \
    --build-arg CONAN_EXTRA_REPOS="conan-local http://$MY_IP:8081/artifactory/api/conan/conan False" \
    --build-arg CONAN_EXTRA_REPOS_USER="user -p password1 -r conan-local admin" \
    --build-arg CONAN_UPLOAD="conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force" \
    --build-arg BUILD_TYPE=Debug \
    -f grpc_conan_source.Dockerfile --tag grpc_conan_repoadd_source_install . --no-cache

sudo -E docker build \
    --build-arg PKG_NAME=grpc_conan/v1.26.x \
    --build-arg PKG_CHANNEL=conan/stable \
    --build-arg PKG_UPLOAD_NAME=grpc_conan/v1.26.x@conan/stable \
    --build-arg CONAN_EXTRA_REPOS="conan-local http://$MY_IP:8081/artifactory/api/conan/conan False" \
    --build-arg CONAN_EXTRA_REPOS_USER="user -p password1 -r conan-local admin" \
    --build-arg CONAN_UPLOAD="conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force" \
    --build-arg BUILD_TYPE=Debug \
    -f grpc_conan_build.Dockerfile --tag grpc_conan_build_package_export_test_upload . --no-cache

# OPTIONAL: clear unused data
sudo -E docker rmi grpc_conan_*
```

## How to run single command in container using bash with gdb support

```bash
# about gdb support https://stackoverflow.com/a/46676907
docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --rm --entrypoint="/bin/bash" -v "$PWD":/home/u/project_copy -w /home/u/project_copy -p 50051:50051 --name DEV_grpc_conan grpc_conan -c pwd
```

## Local build

```bash
export PKG_NAME=grpc_conan/v1.26.x@conan/stable
conan remove $PKG_NAME
conan create . conan/stable -s build_type=Debug --profile gcc --build missing
CONAN_REVISIONS_ENABLED=1 CONAN_VERBOSE_TRACEBACK=1 CONAN_PRINT_RUN_COMMANDS=1 CONAN_LOGGING_LEVEL=10 conan upload $PKG_NAME --all -r=conan-local -c --retry 3 --retry-wait 10 --force

# clean build cache
conan remove "*" --build --force
```

## Conan package recipe for [*grpc*](https://github.com/grpc/grpc)

Google's RPC library and framework.

The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/gaeus/gaeus-conan/grpc%3Agaeus).


## Issues

If you wish to report an issue or make a request for a package, please do so here:

[Issues Tracker](https://github.com/gaeus/conan-grpc/issues)


## For Users

### Basic setup

    $ conan install grpc/1.26.x@gaeus/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    grpc/1.26.x@gaeus/stable

    [generators]
    cmake

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install -s build_type=Debug --build=missing ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

```bash
conan create . gaeus/stable -s build_type=Debug --profile gcc --build=missing

# clean build cache
conan remove "*" --build --force
```

### Available Options
| Option        | Default | Possible Values  |
| ------------- |:----------------- |:------------:|
| fPIC      | True |  [True, False] |
| build_codegen      | True |  [True, False] |
| build_csharp_ext      | False |  [True, False] |


## Add Remote

    $ conan remote add gaeus "https://api.bintray.com/conan/gaeus/gaeus-conan"

## conan upload

    $ export CONAN_REVISIONS_ENABLED=1
    $ conan upload grpc_conan/v1.26.x --all -r=conan-local --retry 3 --retry-wait 10 --parallel --confirm

## How to diagnose errors in conanfile

```bash
# NOTE: about `--keep-source` see https://bincrafters.github.io/2018/02/27/Updated-Conan-Package-Flow-1.1/
CONAN_PRINT_RUN_COMMANDS=1 CONAN_LOGGING_LEVEL=10 CONAN_VERBOSE_TRACEBACK=1 conan create . conan/stable -s build_type=Debug --profile gcc --build missing --keep-source

# clean build cache
conan remove "*" --build --force
```

## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package grpc.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](https://github.com/gaeus/conan-grpc/blob/stable/1.26.x/LICENSE.md)
