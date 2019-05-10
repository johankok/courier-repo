Summary: Courier Unicode Library
Name: courier-unicode
Version: 2.1
Release: 1%{?dist}
License: GPLv3
URL: http://www.courier-mta.org/unicode/
Source: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
BuildRequires: perl-generators
BuildRequires: gcc-c++

%package devel
Summary: Courier Unicode Library development files
Requires: %{name} = 0:%{version}-%{release}

%description
This library implements several algorithms related to the Unicode
Standard.

This package installs only the run-time libraries needed by applications that
use this library. Install the "courier-unicode-devel" package if you want
to develop new applications using this library.

%description devel
This package contains development files for the Courier Unicode Library.
Install this package if you want to develop applications that uses this
unicode library.

%prep
%setup -q
%configure
%build
%{__make} -s %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc README COPYING ChangeLog AUTHORS
%{_libdir}/*.so.*

%files devel
%{_mandir}/*/*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_datadir}/aclocal/*.m4

%changelog
* Sun Jan 12 2014 Sam Varshavchik <mrsam@octopus.email-scan.com> - 1.0
- Initial build.
