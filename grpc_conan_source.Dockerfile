# NOTE:
# Dockerfile follows conan flow
# see https://docs.conan.io/en/latest/developing_packages/package_dev_flow.html
# Dockerfile separates source step from build, e.t.c. using multi-stage builds
# see https://docs.docker.com/develop/develop-images/multistage-build/

# ===
# STAGE FOR CONAN FLOW STEPS:
#   * conan remote add
#   * conan source
#   * conan install
# ===
# allows individual sections to be run by doing: docker build --target ...
FROM conan_build_env as grpc_conan_repoadd_source_install
# NOTE: if not BUILD_GRPC_FROM_SOURCES, then script uses conan protobuf package
ARG BUILD_TYPE=Release
ARG APT="apt-get -qq --no-install-recommends"
ARG LS_VERBOSE="ls -artl"
ARG CONAN="conan"
ARG PKG_NAME="grpc_conan/v1.26.x"
ARG PKG_CHANNEL="conan/stable"
ARG PKG_UPLOAD_NAME="grpc_conan/v1.26.x@conan/stable"
ARG CONAN_SOURCE="conan source"
ARG CONAN_INSTALL="conan install --build missing --profile gcc"
#ARG CONAN_CREATE="conan create --profile gcc"
# Example: conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force --confirm
ARG CONAN_UPLOAD=""
# Example: --build-arg CONAN_EXTRA_REPOS="conan-local http://localhost:8081/artifactory/api/conan/conan False"
ARG CONAN_EXTRA_REPOS=""
# Example: --build-arg CONAN_EXTRA_REPOS_USER="user -p password -r conan-local admin"
ARG CONAN_EXTRA_REPOS_USER=""
ARG CONAN_OPTIONS=""
ENV LC_ALL=C.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    #TERM=screen \
    PATH=/usr/bin/:/usr/local/bin/:/go/bin:/usr/local/go/bin:/usr/local/include/:/usr/local/lib/:/usr/lib/clang/6.0/include:/usr/lib/llvm-6.0/include/:$PATH \
    LD_LIBRARY_PATH=/usr/local/lib/:$LD_LIBRARY_PATH \
    WDIR=/opt \
    # NOTE: PROJ_DIR must be within WDIR
    PROJ_DIR=/opt/project_copy \
    GOPATH=/go \
    CONAN_REVISIONS_ENABLED=1 \
    CONAN_PRINT_RUN_COMMANDS=1 \
    CONAN_LOGGING_LEVEL=10 \
    CONAN_VERBOSE_TRACEBACK=1

# create all folders parent to $PROJ_DIR
RUN set -ex \
  && \
  echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
  && \
  mkdir -p $WDIR

# NOTE: ADD invalidates the cache, COPY does not
COPY "conanfile.py" $PROJ_DIR/conanfile.py
COPY "test_package" $PROJ_DIR/test_package
COPY "build.py" $PROJ_DIR/build.py
COPY "CMakeLists.txt" $PROJ_DIR/CMakeLists.txt
WORKDIR $PROJ_DIR

RUN set -ex \
  && \
  $APT update \
  && \
  cd $PROJ_DIR \
  && \
  $LS_VERBOSE $PROJ_DIR \
  && \
  echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
  && \
  ldconfig \
  && \
  export CC=gcc \
  && \
  export CXX=g++ \
  && \
  if [ ! -z "$CONAN_EXTRA_REPOS" ]; then \
    ($CONAN remote add $CONAN_EXTRA_REPOS || true) \
    ; \
  fi \
  && \
  if [ ! -z "$CONAN_EXTRA_REPOS_USER" ]; then \
    $CONAN $CONAN_EXTRA_REPOS_USER \
    ; \
  fi \
  && \
  $CONAN_SOURCE . \
  && \
  $CONAN_INSTALL -s build_type=$BUILD_TYPE .
