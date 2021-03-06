Summary: Courier Unicode Library
Name: courier-unicode
Version: 2.2.3
Release: 1%{?dist}
License: GPLv3
URL: http://www.courier-mta.org/unicode/
Source0: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
Source1: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2.sig
Source2: courier-unicode.gpg
BuildRequires: perl-interpreter
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: gnupg
BuildRequires: make

%description
This library implements several algorithms related to the Unicode
Standard.

This package installs only the run-time libraries needed by applications that
use this library. Install the "courier-unicode-devel" package if you want
to develop new applications using this library.

%package devel
Summary: Development tools for programs which will use the courier-unicode library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains development files for the Courier Unicode Library.
Install this package if you want to develop applications that uses this
unicode library.

%prep
%setup -q
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'

%build
%configure --disable-static
%{__make} %{?_smp_mflags}

%install
%makeinstall

rm %{buildroot}%{_libdir}/*.la

%check
%{__make} check

%files
%license COPYING
%doc README ChangeLog AUTHORS
%{_libdir}/libcourier-unicode.so.7
%{_libdir}/libcourier-unicode.so.7.0.0

%files devel
%{_includedir}/courier-unicode.h
%{_includedir}/courier-unicode-categories-tab.h
%{_includedir}/courier-unicode-script-tab.h
%{_libdir}/libcourier-unicode.so
%{_datadir}/aclocal/courier-unicode.m4
%{_datadir}/aclocal/courier-unicode-version.m4
%{_mandir}/man3/*
%{_mandir}/man7/*

%changelog
* Sun Apr 04 2021 Johan Kok <johan@fedoraproject.org> - 2.2.3-1
- Bumped to version 2.2.3
- Added make to BuildRequires

* Wed Nov 25 2020 Johan Kok <johan@fedoraproject.org> - 2.1.1-1
- Bumped to version 2.1.1

* Fri May 01 2020 Johan Kok <johan@fedoraproject.org> - 2.1-2
- Validate sources, specify files

* Sun Jan 12 2014 Sam Varshavchik <mrsam@octopus.email-scan.com> - 1.0
- Initial build.
