# If any of the following macros should be set otherwise,
# you can wrap any of them with the following conditions:
# - %%if 0%%{centos} == 7
# - %%if 0%%{?rhel} == 7
# - %%if 0%%{?fedora} == 23
# Or just test for particular distribution:
# - %%if 0%%{centos}
# - %%if 0%%{?rhel}
# - %%if 0%%{?fedora}
#
# Be aware, on centos, both %%rhel and %%centos are set. If you want to test
# rhel specific macros, you can use %%if 0%%{?rhel} && 0%%{?centos} == 0 condition.
# (Don't forget to replace double percentage symbol with single one in order to apply a condition)

# Generate devel rpm
%global with_devel 1
# Build project from bundled dependencies
%global with_bundled 0
# Build with debug info rpm
%global with_debug 0
# Run tests in check section
%global with_check 0
# Generate unit-test rpm
%global with_unit_test 1

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         go-ini
%global repo            ini
# https://github.com/go-ini/ini
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          f55231ca73a76c1d61eb05fe0d64a1ccebf93cba
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global v1_import_path     gopkg.in/v1/ini
%global v1_import_path_sec gopkg.in/ini.v1

Name:           golang-%{provider}-%{project}-%{repo}
Version:        1.39.3
Release:        0.1.git%{shortcommit}%{?dist}
Summary:        Package ini provides INI file read and write functionality in Go
# Detected licences
# - *No copyright* UNKNOWN at 'LICENSE'
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check} && ! 0%{?with_bundled}
%endif

Provides:      golang(%{import_path}) = %{version}-%{release}
Provides:      golang(%{v1_import_path}) = %{version}-%{release}
Provides:      golang(%{v1_import_path_sec}) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test-devel
Summary:         Unit tests for %{name} package
%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%if 0%{?with_check} && ! 0%{?with_bundled}
BuildRequires: golang(github.com/smartystreets/goconvey/convey)
%endif

Requires:      golang(github.com/smartystreets/goconvey/convey)

%description unit-test-devel
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{version}

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
install -d -p %{buildroot}/%{gopath}/src/%{v1_import_path}/
echo "%%dir %%{gopath}/src/%%{v1_import_path}/." >> devel.file-list
install -d -p %{buildroot}/%{gopath}/src/%{v1_import_path_sec}/
echo "%%dir %%{gopath}/src/%%{v1_import_path_sec}/." >> devel.file-list

# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list

    echo "%%dir %%{gopath}/src/%%{v1_import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{v1_import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{v1_import_path}/$file
    echo "%%{gopath}/src/%%{v1_import_path}/$file" >> devel.file-list

    echo "%%dir %%{gopath}/src/%%{v1_import_path_sec}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{v1_import_path_sec}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{v1_import_path_sec}/$file
    echo "%%{gopath}/src/%%{v1_import_path_sec}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test-devel.file-list
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test-devel.file-list
done
cp -r testdata %{buildroot}/%{gopath}/src/%{import_path}/.
echo "%%{gopath}/src/%%{import_path}/testdata" >> unit-test-devel.file-list
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%doc README.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%dir %{gopath}/src/%{v1_import_path}
%dir %{gopath}/src/%{v1_import_path_sec}
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test-devel -f unit-test-devel.file-list
%license LICENSE
%doc README.md
%endif

%changelog
* Fri Aug 16 2019 Martin Mágr <mmagr@redhat.com> - 1.39.3-0.1.git3d73f4b
- Bump to latest upstream release

* Wed Sep 27 2017 Jan Chaloupka <jchaloup@redhat.com> - 1.21.1-0.5.gitf55231c
- Bump to upstream 3d73f4b845efdf9989fffd4b4e562727744a34ba
  related: #1412590

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.21.1-0.4.git6e4869b
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.21.1-0.3.git6e4869b
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.21.1-0.2.git6e4869b
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Jan Chaloupka <jchaloup@redhat.com> - 1.21.1-0.1.git6e4869b
- Bump to upstream 6e4869b434bd001f6983749881c7ead3545887d8
  resolves: #1412590

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.0-0.2.git193d1ec
- https://fedoraproject.org/wiki/Changes/golang1.7

* Thu Apr 14 2016 jchaloup <jchaloup@redhat.com> - 1.9.0-0.1.git193d1ec
- First package for Fedora
  resolves: #1327497
