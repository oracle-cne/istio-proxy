{{{$version := printf "%s.%s.%s" .major .minor .patch }}}
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

{{{$minor_version := printf "%s" .minor }}}
%define minor_version {{{$minor_version}}}

Name:           istio-proxy
Version:        {{{$version}}}
Release:        1%{?dist}
Summary:        The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.
License:        ASL 2.0
Vendor:         Oracle America
URL:            https://github.com/istio/proxy
Source0:        %{name}-%{version}.tar.bz2
{{{- if semverCompare "<1.20.0" $version }}}
Patch0:         Makefile.core.mk.patch
{{{- else if semverCompare "<1.22.0" $version }}}
Patch0:         Makefile.core.mk_1.20.patch
{{{- else if and (semverCompare ">=1.22.0" $version) (semverCompare "<1.23.0" $version) }}}
Patch0:         Makefile.core.mk_1.22.patch
{{{- else if and (semverCompare "<=1.23.0" $version) (semverCompare "<1.24.0" $version) }}}
Patch0:         Makefile.core.mk_1.23.patch
{{{- else if and (semverCompare "<=1.24.0" $version) (semverCompare "<1.25.0" $version) }}}
Patch0:         Makefile.core.mk_1.24.patch
{{{- else }}}
Patch0:         Makefile.core.mk_1.25.patch
{{{- end }}}

{{{- if semverCompare "<1.15.1 || >= 1.16.2" $version }}}
{{{- if semverCompare "<1.22.0" $version }}}
Patch1:         bazelrc_1.20.patch
{{{- else if semverCompare "<1.24.0" $version }}}
Patch1:         bazelrc_1.22.patch
{{{- else if semverCompare "<1.25.0" $version }}}
Patch1:         bazelrc_1.24.patch
{{{- else }}}
Patch1:         bazelrc_1.25.patch
{{{- end }}}
{{{- end }}}

{{{- if semverCompare ">=1.29.0" $version }}}
Patch2:         WORKSPACE_1.25.patch
{{{- end }}}

{{{- if semverCompare "<1.22.0" $version }}}
BuildRequires:  lld = 9.0.1
BuildRequires:  llvm-toolset = 9.0.1
BuildRequires:  clang = 9.0.1
{{{- else if semverCompare "<1.29.0" $version }}}
BuildRequires:  lld = 13.0.1
BuildRequires:  llvm-toolset = 13.0.1
BuildRequires:  clang = 13.0.1
{{{- else }}}
BuildRequires:  lld = 18.1.8
BuildRequires:  llvm-toolset = 18.1.8
BuildRequires:  clang = 18.1.8
{{{- end }}}
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  autoconf-archive
BuildRequires:  autogen
BuildRequires:  libtool
{{{- if semverCompare ">=1.31.0" $version }}}
BuildRequires:  gcc-toolset-13-libatomic-devel
{{{- else }}}
BuildRequires:  libatomic-static
{{{- end }}}
BuildRequires:  libstdc++-static
BuildRequires:  libstdc++-devel
BuildRequires:  gcc-c++
BuildRequires:  perl
BuildRequires:  cmake3 = 3.11.4
BuildRequires:  python2
BuildRequires:  python3
BuildRequires:  git
{{{- if semverCompare "<1.29.0" $version }}}
BuildRequires:  java-11-openjdk-devel
{{{- else }}}
BuildRequires:  java-21-openjdk-devel
{{{- end }}}
BuildRequires:  tzdata-java
{{{- if and (semverCompare ">=1.18.0" $version) (semverCompare "<1.22.0" $version) }}}
BuildRequires:  bazel = 6.3.2
{{{- else if semverCompare "<1.29.0" $version }}}
BuildRequires:  bazel = 6.5.0
{{{- else if semverCompare "<1.31.0" $version }}}
BuildRequires:  bazel = 7.7.1
{{{- else }}}
BuildRequires:  bazel = 8.7.0
{{{- end }}}
BuildRequires:  ninja-build
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  golang
BuildRequires:  wget
BuildRequires:  ncurses-compat-libs


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
{{{- if semverCompare "<1.15.1 || >= 1.16.2" $version }}}
%patch1
{{{- end }}}
{{{- if semverCompare ">=1.29.0" $version }}}
%patch2
{{{- end }}}

%build
alternatives --set python /usr/bin/python2
{{{- if semverCompare "<1.29.0" $version }}}
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
{{{- else }}}
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
{{{- end }}}
export GOROOT=/usr/bin/go

{{{- if or (semverCompare "<1.10" $version) (semverCompare ">=1.15.0" $version) }}}
echo "Querying istio-envoy {{{.major}}}.{{{.minor}}} source RPM versions"
envoy_src_rpm_version=$(repoquery --show-duplicates 'istio-envoy-{{{.major}}}.{{{.minor}}}.*' -q --qf "%%{version}-%%{release}" | tail -1)
if [ -z "${envoy_src_rpm_version}" ]; then
echo "No matching istio-envoy-{{{.major}}}.{{{.minor}}}.* package found in configured repositories" >&2
exit 1
fi
envoy_src_rpm="istio-envoy-${envoy_src_rpm_version}"
envoy_src_dir="istio-envoy-${envoy_src_rpm_version%%-*}"
envoy_src_tar="${envoy_src_dir}.tar.bz2"
echo "Selected istio-envoy source RPM: ${envoy_src_rpm}"
echo "Expected istio-envoy source archive inside RPM: ${envoy_src_tar}"
yumdownloader --source "${envoy_src_rpm}"
echo "Extracting ${envoy_src_tar} from ${envoy_src_rpm} source RPM"
rpm2cpio "${envoy_src_rpm}"*.rpm | cpio -iv --to-stdout "${envoy_src_tar}" > "${envoy_src_tar}"
if [ ! -s "${envoy_src_tar}" ]; then
echo "Failed to extract non-empty ${envoy_src_tar} from ${envoy_src_rpm} source RPM" >&2
echo "Source RPM contents:" >&2
rpm2cpio "${envoy_src_rpm}"*.rpm | cpio -t >&2
exit 1
fi
echo "Validating ${envoy_src_tar}"
bzip2 -t "${envoy_src_tar}"
echo "Unpacking ${envoy_src_tar}"
tar -xjf "${envoy_src_tar}"

export LOCAL_ENVOY_PROJECT=${PWD}/${envoy_src_dir}
echo "Using Envoy source directory: ${LOCAL_ENVOY_PROJECT}"
{{{- end }}}

{{{- if and (semverCompare ">=1.22.0" $version) (semverCompare "<1.29.0" $version) }}}
ln -s /usr/lib64/libatomic.so.1.2.0 /usr/lib64/libatomic.so
{{{- end }}}

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
* {{{.changelog_timestamp}}} - {{{$version}}}-1
- Added Oracle Specific Build Files for istio/proxy
