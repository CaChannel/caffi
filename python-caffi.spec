Name: python-caffi
Summary: Channel Access Foreign Function Interface
Version: 1.0.3
Release: 1%{?dist}
Source0: https://pypi.io/packages/source/c/caffi/caffi-%{version}.tar.gz
License: BSD
Group: Development/Libraries
Vendor: Xiaoqiang Wang <xiaoqiang.wang AT psi DOT ch>
Url: https://github.com/CaChannel/caffi

BuildRequires: python-setuptools
Requires: python-cffi python-enum34

# Do not check .so files in the python_sitelib directory
# or any files in the application's directory for provides
%global __provides_exclude_from ^%{python_sitelib}/.*\\.so$
%global __requires_exclude_from ^%{python_sitelib}/.*\\.so$
%global _unpackaged_files_terminate_build      0
%global _binaries_in_noarch_packages_terminate_build   0

%description
caffi
=====

caffi is the Channel Access Foreign Function Interface.
It uses `CFFI <https://pypi.python.org/pypi/cffi>`_ to call EPICS channel access library.

This package provides direct low level interface to channel access, alike the C API.

%prep

%setup -n caffi-%{version}

%build
# remove libraries for other platform
rm -fr caffi/lib/darwin-x86
rm -fr caffi/lib/win32-x86
rm -fr caffi/lib/windows-x64
rm -fr caffi/lib/linux-x86
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
