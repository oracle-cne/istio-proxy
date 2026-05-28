#!/bin/bash -ex

function version { echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }'; }

istio_version=${1}
# Link ninja-build because envoy expects the binary name to be `ninja`. Using a Link to ensure
# subsequent bash shells also have the mapping
if [ ! -f /usr/bin/ninja ]; then
  ln /usr/bin/ninja-build /usr/bin/ninja
fi

cpu_count="18"
if [[ $(version $istio_version) -ge $(version "1.18.0") ]]; then
    # Reduced cpu_count/parallelism to avoid build failures on running out of memory
    cpu_count="16"
fi

BAZEL_BUILD=' --local_cpu_resources='$cpu_count' --copt=-DENVOY_IGNORE_GLIBCXX_USE_CXX11_ABI_ERROR=1 --verbose_failures --copt=-DNDEBUG '
ENVOY_REPO=--override_repository=envoy="${LOCAL_ENVOY_PROJECT}"
BAZEL_BUILD_ARGS="$ENVOY_REPO$BAZEL_BUILD"
BAZEL_BUILD_LOG="/tmp/build.log"
export BAZEL_BUILD_ARGS

if [[ -f ~/.npmrc ]]; then
    cp -f ~/.npmrc /mnt/.npmrc
fi
export HOME=/mnt

ENVOY_BIN=./bazel-bin/src/envoy/envoy
if [[ $(version $istio_version) -ge $(version "1.17.0") ]]; then
    ENVOY_BIN=./bazel-bin/envoy
fi

# Build istio proxy
## Added workaround for jenkins build failure,
## 'FATAL: Attempted to kill stale server process (pid=365) using SIGKILL, but it did not die in a timely fashion.'
nohup make VERBOSE=1 build -j${cpu_count} > $BAZEL_BUILD_LOG 2>&1 | tail -f $BAZEL_BUILD_LOG &
# There are 'build success' messages in-between, so, check the last line of log file for success completion.
# And, precense of envoy binary doesn't mean the build completion.
while [[ ! (((-f $ENVOY_BIN) \
                && $(tail -n 2 $BAZEL_BUILD_LOG|grep "Build completed successfully")) \
        || $(cat $BAZEL_BUILD_LOG | grep "Build did NOT complete successfully")) ]]; do
    sleep 60
done

set +e
ps ax | grep bazel | grep -v color=auto | awk '{print $1}'|xargs kill -9
set -e
