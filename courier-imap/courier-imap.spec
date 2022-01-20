Summary: Courier IMAP server
Name: courier-imap
Version: 5.1.7
Release: 1%{?dist}
License: GPLv3
URL: http://www.courier-mta.org/imap/
Source0: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
Source1: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2.sig
Source2: courier-imap.gpg
Requires: coreutils sed
Requires(post):   systemd
Requires(postun):   systemd
Requires(preun):  systemd
Requires: courier-authlib >= 0.60.6.20080629
BuildRequires: procps
BuildRequires: coreutils
BuildRequires: courier-authlib-devel >= 0.60.6.20080629
BuildRequires: libidn-devel
BuildRequires: courier-unicode-devel
BuildRequires: gdbm-devel
BuildRequires: gcc-c++
BuildRequires: pcre2-devel
BuildRequires: valgrind

BuildRequires: openssl
BuildRequires: openssl-devel

BuildRequires: perl-interpreter
BuildRequires: gnupg
BuildRequires: make

%if 0%{?fedora} >= 30 || 0%{?rhel} >= 8
BuildRequires: glibc-all-langpacks
%endif

#  RH 7.0 resets sysconfdir & mandir, put them back where they belong

%define _sysconfdir %{_prefix}/etc
%define	_mandir %{_prefix}/man

%define	_prefix	/usr/lib/courier-imap

%define _localstatedir /var/run

%define initdir %(if test -d /etc/init.d/. ; then echo /etc/init.d ; else echo /etc/rc.d/init.d ; fi)

%define pamconfdir	/etc/pam.d

%description
Courier-IMAP is an IMAP server for Maildir mailboxes.  This package contains
the standalone version of the IMAP server that is included in the Courier
mail server package.  This package is a standalone version for use with
other mail servers.  Do not install this package if you intend to install the
full Courier mail server. Install the Courier package instead.

%prep
%autosetup
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'

%build
%configure --with-notice=unicode
%{__make} %{_smp_mflags}

%check
%{__make} check

%install
%{__mkdir_p} $RPM_BUILD_ROOT%{pamconfdir}
%{__mkdir_p} $RPM_BUILD_ROOT%{initdir}
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}
%{__mkdir_p} $RPM_BUILD_ROOT/lib/systemd/system

install -Dm 755 packaging/systemd/courier-imap.sysvinit $RPM_BUILD_ROOT/%{_datadir}
install -Dm 644 packaging/systemd/courier-imap.service $RPM_BUILD_ROOT/lib/systemd/system

cat >$RPM_BUILD_ROOT/%{_datadir}/dhparams.pem.dist <<ZZ
This file contains default DH parameters for initial use on a new
installation. The startup script copies this file to dhparams.pem,
unless it already exists.

ZZ

sed 's/^chown/echo/' <libs/imap/mkdhparams >libs/imap/mkdhparams.tmp
TLS_DHPARAMS=$RPM_BUILD_ROOT/%{_datadir}/dhparams.pem.dist.tmp %{__spec_rmbuild_shell} libs/imap/mkdhparams.tmp
rm -f libs/imap/mkdhparams.tmp
cat $RPM_BUILD_ROOT/%{_datadir}/dhparams.pem.dist.tmp >>$RPM_BUILD_ROOT/%{_datadir}/dhparams.pem.dist
rm -f $RPM_BUILD_ROOT/%{_datadir}/dhparams.pem.dist.tmp

%{__mkdir_p} $RPM_BUILD_ROOT/etc/cron.monthly
%{__ln_s} %{_sbindir}/mkdhparams $RPM_BUILD_ROOT/etc/cron.monthly/courier-imap-mkdhparams

#
# Fix imapd.dist
#

%{__sed} 's/^IMAPDSTART=.*/IMAPDSTART=YES/' \
  <$RPM_BUILD_ROOT%{_sysconfdir}/imapd.dist \
  >$RPM_BUILD_ROOT%{_sysconfdir}/imapd.dist.tmp

%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/imapd.dist.tmp \
  $RPM_BUILD_ROOT%{_sysconfdir}/imapd.dist

%{__sed} 's/^IMAPDSSLSTART=.*/IMAPDSSLSTART=YES/' \
  <$RPM_BUILD_ROOT%{_sysconfdir}/imapd-ssl.dist \
  >$RPM_BUILD_ROOT%{_sysconfdir}/imapd-ssl.dist.tmp

%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/imapd-ssl.dist.tmp \
  $RPM_BUILD_ROOT%{_sysconfdir}/imapd-ssl.dist

%{__chmod} 600 $RPM_BUILD_ROOT%{_sysconfdir}/imapd.dist
%{__chmod} 600 $RPM_BUILD_ROOT%{_sysconfdir}/imapd-ssl.dist

%{__sed} 's/^POP3DSTART=.*/POP3DSTART=YES/' \
  <$RPM_BUILD_ROOT%{_sysconfdir}/pop3d.dist \
  >$RPM_BUILD_ROOT%{_sysconfdir}/pop3d.dist.tmp

%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/pop3d.dist.tmp \
  $RPM_BUILD_ROOT%{_sysconfdir}/pop3d.dist

%{__sed} 's/^POP3DSSLSTART=.*/POP3DSSLSTART=YES/' \
  <$RPM_BUILD_ROOT%{_sysconfdir}/pop3d-ssl.dist \
  >$RPM_BUILD_ROOT%{_sysconfdir}/pop3d-ssl.dist.tmp

%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/pop3d-ssl.dist.tmp \
  $RPM_BUILD_ROOT%{_sysconfdir}/pop3d-ssl.dist

%{__chmod} 600 $RPM_BUILD_ROOT%{_sysconfdir}/pop3d.dist
%{__chmod} 600 $RPM_BUILD_ROOT%{_sysconfdir}/pop3d-ssl.dist

#
# Red Hat /etc/profile.d scripts
#

%{__mkdir_p} $RPM_BUILD_ROOT/etc/profile.d
%{__cat} >$RPM_BUILD_ROOT/etc/profile.d/courier-imap.sh <<EOF
if echo "\$MANPATH" | tr ':' '\012' | fgrep -qx %{_mandir}
then
  :
else
  MANPATH="%{_mandir}:\$MANPATH"
  export MANPATH
  PATH="%{_bindir}:\$PATH"
  if test -w /etc
  then
    PATH="%{_sbindir}:\$PATH"
  fi
  export PATH
fi
EOF

%{__cat} >$RPM_BUILD_ROOT/etc/profile.d/courier-imap.csh <<EOF

if ( \$?MANPATH ) then
  true
else
  setenv MANPATH ""
endif

echo "\$MANPATH" | tr ':' '\012' | fgrep -qx %{_mandir}

if ( \$? ) then
  true
else
  setenv MANPATH "%{_mandir}:\$MANPATH"
  setenv PATH "%{_bindir}:\$PATH"
  test -w /etc
  if ( \$? ) then
    true
  else
    setenv PATH "%{_sbindir}:\$PATH"
  endif
endif
EOF

%{__cp} libs/imap/README README.imap
%{__cp} libs/imap/README.proxy* .
%{__cp} libs/maildir/README.maildirquota.txt README.maildirquota
%{__cp} libs/maildir/README.sharedfolders.txt README.sharedfolders

####
## Create config files for sysconftool-rpmupgrade (see below)

mkdir -p $RPM_BUILD_ROOT%{_datadir}
%{__cp} -f sysconftool $RPM_BUILD_ROOT%{_datadir}/sysconftool
%{__chmod} 555 $RPM_BUILD_ROOT%{_datadir}/sysconftool
%{__cat} >$RPM_BUILD_ROOT%{_datadir}/configlist <<EOF
%{_sysconfdir}/imapd.dist
%{_sysconfdir}/imapd-ssl.dist
%{_sysconfdir}/pop3d.dist
%{_sysconfdir}/pop3d-ssl.dist
EOF

%{__chmod} 644 $RPM_BUILD_ROOT%{_datadir}/configlist*

%{__mkdir_p} $RPM_BUILD_ROOT%{_localstatedir}
touch $RPM_BUILD_ROOT%{_localstatedir}/imapd.pid
touch $RPM_BUILD_ROOT%{_localstatedir}/imapd-ssl.pid
touch $RPM_BUILD_ROOT%{_localstatedir}/imapd.pid.lock
touch $RPM_BUILD_ROOT%{_localstatedir}/imapd-ssl.pid.lock

touch $RPM_BUILD_ROOT%{_localstatedir}/pop3d.pid
touch $RPM_BUILD_ROOT%{_localstatedir}/pop3d-ssl.pid
touch $RPM_BUILD_ROOT%{_localstatedir}/pop3d.pid.lock
touch $RPM_BUILD_ROOT%{_localstatedir}/pop3d-ssl.pid.lock

%post
if test -f %{initdir}/courier-imap
then
# Update to systemd

  /sbin/chkconfig --del courier-imap || :
  /bin/systemctl stop courier-imap.service || :
fi
%{_datadir}/sysconftool `%{__cat} %{_datadir}/configlist` >/dev/null
%systemd_post courier-imap.service
if [ $1 -eq 1 ]
then
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if test "$1" = "0"
then
  rm -f %{_localstatedir}/couriersslcache
fi
%systemd_preun courier-imap.service

%postun
%systemd_postun_with_restart courier-imap.service

%files
%defattr(-, bin, bin)
/etc/cron.monthly/*
%attr(644, root, root) %config(noreplace) %{pamconfdir}/imap
%attr(644, root, root) %config(noreplace) %{pamconfdir}/pop3

%attr(755, bin, bin) %config /etc/profile.d/courier-imap.csh
%attr(755, bin, bin) %config /etc/profile.d/courier-imap.sh
%attr(-, root, root) /lib/systemd/system/*
%{_datadir}/courier-imap.sysvinit
%dir %{_prefix}

%if "%{_prefix}" != "%{_exec_prefix}"
%dir %{_exec_prefix}
%endif

%{_libexecdir}
%dir %{_sysconfdir}
%dir %{_sysconfdir}/shared
%dir %{_sysconfdir}/shared.tmp

%config %{_sysconfdir}/imap*
%config %{_sysconfdir}/pop3*
%config %{_sysconfdir}/quotawarnmsg.example
%{_bindir}
%{_sbindir}
%{_mandir}
%dir %{_datadir}
%{_datadir}/configlist
%{_datadir}/mk*
%{_datadir}/sysconftool
%attr(600, root, root) %{_datadir}/dhparams.pem.dist

%doc NEWS AUTHORS COPYING libs/imap/BUGS README README.imap README.maildirquota
%doc README.sharedfolders
%doc README.proxy*

%ghost %attr(600, root, root) %{_localstatedir}/imapd.pid
%ghost %attr(600, root, root) %{_localstatedir}/imapd-ssl.pid
%ghost %attr(600, root, root) %{_localstatedir}/imapd.pid.lock
%ghost %attr(600, root, root) %{_localstatedir}/imapd-ssl.pid.lock

%ghost %attr(600, root, root) %{_localstatedir}/pop3d.pid
%ghost %attr(600, root, root) %{_localstatedir}/pop3d-ssl.pid
%ghost %attr(600, root, root) %{_localstatedir}/pop3d.pid.lock
%ghost %attr(600, root, root) %{_localstatedir}/pop3d-ssl.pid.lock

%changelog
* Thu Jan 20 2022 Johan Kok <johan@fedoraproject.org> - 5.1.7-1
- Bumped to version 5.1.7
- Added BuildRequires on PCRE2 and valgrind

* Fri Oct 15 2021 Johan Kok <johan@fedoraproject.org> - 5.1.4-1
- Bumped to version 5.1.4

* Mon Apr 26 2021 Johan Kok <johan@fedoraproject.org> - 5.1.3-1
- Bumped to version 5.1.3

* Sun Apr 04 2021 Johan Kok <johan@fedoraproject.org> - 5.1.2-1
- Bumped to version 5.1.2
- Added make to BuildRequires
