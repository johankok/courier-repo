Name: courier-authlib
Version: 0.71.3
Release: 1%{?dist}
Summary: Courier authentication library

License: GPLv3
URL: http://www.courier-mta.org/authlib/

Source0: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
Source1: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2.sig
Source2: courier-authlib.gpg

BuildRequires: libtool
BuildRequires: openldap-devel
BuildRequires: mysql-devel
BuildRequires: zlib-devel
BuildRequires: sqlite-devel
BuildRequires: postgresql-devel
BuildRequires: gdbm-devel
BuildRequires: pam-devel
BuildRequires: expect
BuildRequires: gcc-c++
BuildRequires: courier-unicode-devel
BuildRequires: procps
BuildRequires: gnupg
BuildRequires: make
BuildRequires: perl-generators

BuildRequires: libtool-ltdl-devel

Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):    systemd

%description
The Courier authentication library provides authentication services for
other Courier applications.

%package devel
Summary:  Development libraries for the Courier authentication library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the development libraries and files needed to compile
Courier packages that use this authentication library.  Install this
package in order to build the rest of the Courier packages.  After they are
built and installed this package can be removed.  Files in this package
are not needed at runtime.

%package userdb
Summary:  Userdb support for the Courier authentication library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description userdb
This package installs the userdb support for the Courier authentication
library.  Userdb is a simple way to manage virtual mail accounts using
a GDBM-based database file.
Install this package in order to be able to authenticate with userdb.

%package ldap
Summary:  LDAP support for the Courier authentication library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description ldap
This package installs LDAP support for the Courier authentication library.
Install this package in order to be able to authenticate using LDAP.

%package mysql
Summary:  MySQL support for the Courier authentication library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description mysql
This package installs MySQL support for the Courier authentication library.
Install this package in order to be able to authenticate using MySQL.

%package sqlite
Summary:  SQLite support for the Courier authentication library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description sqlite
This package installs SQLite support for the Courier authentication library.
Install this package in order to be able to authenticate using an SQLite-based
database file.

%package pgsql
Summary:  PostgreSQL support for the Courier authentication library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description pgsql
This package installs PostgreSQL support for the Courier authentication
library.
Install this package in order to be able to authenticate using PostgreSQL.

%package pipe
Summary:  External authentication module that communicates via pipes
Requires: %{name}%{?_isa} = %{version}-%{release}

%description pipe
This package installs the authpipe module, which is a generic plugin
that enables authentication requests to be serviced by an external
program, then communicates through messages on stdin and stdout.

%prep
%setup -q
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'

%build
%configure
%{__make} %{_smp_mflags}

%check
%{__make} check

%install
MAKEFLAGS= %{__make} -j 1 install DESTDIR=$RPM_BUILD_ROOT
%{__rm} -f $RPM_BUILD_ROOT%{_libdir}/courier-authlib/*.a
%{__install} -m 555 sysconftool $RPM_BUILD_ROOT%{_libexecdir}/courier-authlib

./courierauthconfig --configfiles >configtmp
. ./configtmp

d=`pwd`
cd $RPM_BUILD_ROOT%{_localstatedir}/spool/authdaemon || exit 1
$d/authmksock ./socket || exit 1
cd $d || exit 1
touch $RPM_BUILD_ROOT%{_localstatedir}/spool/authdaemon/pid.lock || exit 1
touch $RPM_BUILD_ROOT%{_localstatedir}/spool/authdaemon/pid || exit 1
%{__chmod} 777 $RPM_BUILD_ROOT%{_localstatedir}/spool/authdaemon/socket || exit 1

cat >configfiles.base <<EOF
%defattr(-,$mailuser,$mailgroup,-)
%{_sysconfdir}/authlib
%{_libexecdir}/courier-authlib
%dir %{_libdir}/courier-authlib
%dir %attr(750,$mailuser,$mailgroup) %{_localstatedir}/spool/authdaemon
EOF

echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.mysql
echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.sqlite
echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.ldap
echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.pgsql
echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.userdb
echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.pipe
echo "%defattr(-,$mailuser,$mailgroup,-)" >configfiles.devel

for f in $RPM_BUILD_ROOT%{_sbindir}/*
do
	fn=`basename $f`
	case "$fn" in
	*userdb*)
		echo "%{_sbindir}/$fn" >>configfiles.userdb
		;;
	*)
		echo "%{_sbindir}/$fn" >>configfiles.base
		;;
	esac
done

for f in $RPM_BUILD_ROOT%{_libdir}/courier-authlib/*
do
	fn=`basename $f`

	# Remove *.la for authentication modules, keep the ones
	# for client libraries. Do this before we sort them into buckets,
	# below.

	case "$fn" in
	*.la)
		case "$fn" in
		libcourierauth*)
			;;
		*)
			rm -f "$f"
			;;
		esac
		continue
		;;
	esac

	case "$fn" in
		*.so)
			case "$fn" in
			libcourierauth*)
				;;
			*)
				rm -f "$f"
				continue
				;;
			esac
			;;
		esac

	case "$fn" in
	libauthpipe*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.pipe
		;;
	libauthldap*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.ldap
		;;
	libauthmysql*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.mysql
		;;
	libauthsqlite*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.sqlite
		;;
	libauthpgsql*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.pgsql
		;;
	libauthldap*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.ldap
		;;
	libauthuserdb*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.userdb
		;;
	*.so)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.devel
		;;
	*)
		echo "%{_libdir}/courier-authlib/$fn" >>configfiles.base
		;;
	esac
done
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}
%{__install} -m 555 courier-authlib.sysvinit $RPM_BUILD_ROOT%{_datadir}

%{__mkdir_p} $RPM_BUILD_ROOT/lib/systemd/system
%{__install} -m 644 courier-authlib.service $RPM_BUILD_ROOT/lib/systemd/system

%post
%{_libexecdir}/courier-authlib/sysconftool %{_sysconfdir}/authlib/*.dist >/dev/null
if test -f /etc/init.d/courier-authlib
then
# Upgrade to systemd

        /sbin/chkconfig --del courier-authlib
        /bin/systemctl stop courier-authlib.service || :
fi
%systemd_post courier-authlib.service
if [ $1 -eq 1 ]
then
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if test "$1" = "0"
then
%systemd_preun courier-authlib.service
fi

%postun
if [ $1 -eq 0 ]
then
    /bin/systemctl daemon-reload
fi
%systemd_postun_with_restart courier-authlib.service

%files -f configfiles.base
%defattr(-,root,root,-)
%doc README README*html README.authmysql.myownquery README.ldap
%doc NEWS AUTHORS ChangeLog
%license COPYING COPYING.GPL
/lib/systemd/system/*
%attr(755, bin, bin) %{_datadir}/courier-authlib.sysvinit
%ghost %attr(600, root, root) %{_localstatedir}/spool/authdaemon/pid.lock
%ghost %attr(644, root, root) %{_localstatedir}/spool/authdaemon/pid
%ghost %attr(-, root, root) %{_localstatedir}/spool/authdaemon/socket
%{_mandir}/man1/*

%files -f configfiles.userdb userdb
%{_mandir}/man8/*userdb*

%files -f configfiles.devel devel
%defattr(-,root,root,-)
%{_bindir}/courierauthconfig
%{_includedir}/*
%{_mandir}/man3/*
%{_libdir}/courier-authlib/*.la
%doc authlib.html auth_*.html

%files -f configfiles.ldap ldap
%defattr(-,root,root,-)
%doc authldap.schema authldap.ldif

%files -f configfiles.mysql mysql

%files -f configfiles.sqlite sqlite

%files -f configfiles.pgsql pgsql

%files -f configfiles.pipe pipe

%changelog
* Tue Apr 13 2021 Johan Kok <johan@fedoraproject.org> - 0.71.3-1
- Bumped to version 0.71.3
- Use perl-generators for sysconftool perl dependencies

* Sun Apr 04 2021 Johan Kok <johan@fedoraproject.org> - 0.71.2-1
- Bumped to version 0.71.2
- Added make to BuildRequires

* Thu Sep  7 2006 Chris Petersen <rpm@forevermore.net>                  0.58-2
- Make the spec a little prettier
- Replace BuildPreReq with BuildRequires
- Remove period from summaries (rpmlint)
- Fix release tag to use %{?dist} macro if it's present
- Change distro-detection to use "rh" and "fc" for version detection, and add support for mandriva

* Sun Oct  3 2004 Mr. Sam <sam@email-scan.com>                          0.50-1
- Initial build.
