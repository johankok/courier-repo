#
# Copyright 1998 - 2010 Double Precision, Inc.  See COPYING for
# distribution information.

Summary: Maildrop mail filter/mail delivery agent
Name: maildrop
Version: 3.0.0
Release: 1%{?dist}
License: GPLv3
Group: Applications/Internet
Source: https://downloads.sourceforge.net/courier/%{name}-%{version}.tar.bz2
Url: http://www.courier-mta.org/maildrop/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: /usr/include/fam.h gdbm-devel pcre-devel
BuildRequires: libidn-devel
BuildRequires: courier-unicode-devel
BuildRequires: gcc-c++

%package devel
Summary: development tools for handling E-mail messages
Group: Applications/Mail

%package man
Summary: manual pages for maildrop
Group: Applications/Mail

%description

Maildrop is a combination mail filter/mail delivery agent.
Maildrop reads the message to be delivered to your mailbox,
optionally reads instructions from a file how filter incoming
mail, then based on these instructions may deliver mail to an
alternate mailbox, or forward it, instead of dropping the
message into your mailbox.

Maildrop uses a structured, real, meta-programming language in
order to define filtering instructions.  Its basic features are
fast and efficient.  At sites which carry a light load, the
more advanced, CPU-demanding, features can be used to build
very sophisticated mail filters.  Maildrop deployments have
been reported at sites that support as many as 30,000
mailboxes.

Maildrop mailing list:
http://lists.sourceforge.net/lists/listinfo/courier-maildrop

This version is compiled with support for GDBM database files,
maildir enhancements (folders+quotas), and userdb.

%description devel
The maildrop-devel package contains the libraries and header files
that can be useful in developing software that works with or processes
E-mail messages.

Install the maildrop-devel package if you want to develop applications
which use or process E-mail messages.

%description man
This package contains manual pages for maildrop and associated
utilities.
%prep

%setup -q
%configure --with-devel --enable-userdb --enable-maildirquota --enable-syslog=1 --enable-trusted-users='root mail daemon postmaster qmaild mmdf' --enable-restrict-trusted=0 --enable-sendmail=/usr/sbin/sendmail

%build

%{__make} %{_smp_mflags}
%install

rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT MAILDROPUID='' MAILDROPGID=''

mkdir htmldoc
cp $RPM_BUILD_ROOT%{_docdir}/*/html/* htmldoc
rm -rf $RPM_BUILD_ROOT%{_docdir}/*/html

%files
%defattr(-, bin, bin)

%doc htmldoc/*

%attr(555, root, mail) %{_bindir}/maildrop
%attr(555, root, mail) %{_bindir}/lockmail
%{_bindir}/mailbot
%{_bindir}/maildirmake
%{_bindir}/deliverquota
%{_bindir}/reformail
%{_bindir}/makemime
%{_bindir}/reformime
%{_bindir}/makedat
%{_bindir}/makedatprog

%doc libs/maildir/README.maildirquota.html libs/maildir/README.maildirquota.txt
%doc COPYING README README.postfix INSTALL NEWS UPGRADE ChangeLog maildroptips.txt

%files devel
%defattr(-, bin, bin)
%{_mandir}/man3/*
%{_includedir}/*
%{_libdir}/lib*

%files man
%defattr(-, bin, bin)
%{_mandir}/man[1578]/*

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
