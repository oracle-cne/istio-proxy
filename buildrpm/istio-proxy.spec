
# Generate devel rpm
%global with_devel 0
# Build with debug info rpm
%global with_debug 0

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global envoy_libdir /var/lib/istio/envoy
%global _buildhost   build-ol%{?oraclelinux}-%{?_arch}.oracle.com


%define minor_version 27

Name:           istio-proxy
Version:        1.27.3
Release:        1%{?dist}
Summary:        The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.
License:        ASL 2.0
Vendor:         Oracle America
URL:            https://github.com/istio/proxy
Source0:        %{name}-%{version}.tar.bz2
Patch0:         Makefile.core.mk_1.25.patch
Patch1:         bazelrc_1.25.patch
BuildRequires:  lld = 13.0.1
BuildRequires:  llvm-toolset = 13.0.1
BuildRequires:  clang = 13.0.1
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  autogen
BuildRequires:  libtool
BuildRequires:  libatomic-static
BuildRequires:  libstdc++-static
BuildRequires:  gcc-c++
BuildRequires:  perl
BuildRequires:  cmake3 = 3.11.4
BuildRequires:  python2
BuildRequires:  python3
BuildRequires:  git
BuildRequires:  java-11-openjdk-devel
BuildRequires:  tzdata-java
BuildRequires:  bazel = 6.5.0
BuildRequires:  ninja-build
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  golang
BuildRequires:  wget


%description
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

########### istio-proxy ###############
%package proxy
Summary:  The istio envoy proxy

%description proxy
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

This package contains the envoy program.

proxy is the proxy required by the Istio Pilot Agent that talks to Istio pilot

%prep
%setup -q -n %{name}-%{version}
%patch0
%patch1

%build
alternatives --set python /usr/bin/python2
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
export GOROOT=/usr/bin/go
mkdir -p /tmp/envoy-src
envoy_src_rpm_version=$(repoquery --show-duplicates  istio-envoy-1.27.*  -q --qf "%{version}" | tail -1)
envoy_src_rpm="istio-envoy-${envoy_src_rpm_version}"
pushd /tmp/envoy-src
yumdownloader --source istio-envoy-%{version}-%{release}
rpm2cpio ${envoy_src_rpm}*.rpm|cpio -iv --to-stdout ${envoy_src_rpm}.tar.bz2 > ${envoy_src_rpm}.tar.bz2
tar -xjvf ${envoy_src_rpm}.tar.bz2
popd

export LOCAL_ENVOY_PROJECT=/tmp/envoy-src/${envoy_src_rpm}
ln -s /usr/lib64/libatomic.so.1.2.0 /usr/lib64/libatomic.so

chmod +x build_istio_proxy.sh
./build_istio_proxy.sh %{version}

%install
rm -rf ${RPM_BUILD_ROOT}
install -d -m755 ${RPM_BUILD_ROOT}/usr/local/bin
install -d -m755 ${RPM_BUILD_ROOT}%{envoy_libdir}

function version { echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }'; }

if [[ $(version "%{version}") -ge $(version "1.17.0") ]]; then
cp -pav ./bazel-bin/envoy ${RPM_BUILD_ROOT}/usr/local/bin
else
cp -pav ./bazel-bin/src/envoy/envoy ${RPM_BUILD_ROOT}/usr/local/bin
fi

%files
/usr/local/bin/envoy
%license LICENSE THIRD_PARTY_LICENSES.txt

%changelog
* Tue Oct 21 2025 Oracle Cloud Native Environment Authors <noreply@oracle.com> - 1.27.3-1
- Added Oracle Specific Build Files for istio/proxy
