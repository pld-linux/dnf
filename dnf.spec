#
# Conditional build:
%bcond_without	tests		# build without tests
#
# TODO
# - bash-completion subpackage
# - make -DSYSTEMD_DIR actually to work: https://github.com/rpm-software-management/dnf/pull/213
%define	gitrev a7e0aa1
%define	hawkey_version 0.5.2
%define	librepo_version 1.7.5
%define	libcomps_version 0.1.6
%define	rpm_version 5.4.0

Summary:	Package manager forked from Yum, using libsolv as a dependency resolver
Name:		dnf
Version:	0.6.3
Release:	0.5
Group:		Base
# For a breakdown of the licensing, see PACKAGE-LICENSING
License:	GPL v2+ and GPL v2 and GPL
#Source0:	http://rpm-software-management.fedorapeople.org/%{name}-%{gitrev}.tar.xz
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/dnf/%{name}-%{gitrev}.tar.xz/82ff495e445ddc56e70dc91750a421ac/dnf-%{gitrev}.tar.xz
# Source0-md5:	82ff495e445ddc56e70dc91750a421ac
Patch0:		rpm5.patch
URL:		https://github.com/rpm-software-management/dnf
BuildRequires:	cmake
BuildRequires:	gettext
BuildRequires:	gettext-tools
BuildRequires:	python
BuildRequires:	python-Sphinx
#BuildRequires:	python-bugzilla
BuildRequires:	python-hawkey >= %{hawkey_version}
BuildRequires:	python-iniparse
BuildRequires:	python-libcomps >= %{libcomps_version}
BuildRequires:	python-librepo >= %{librepo_version}
BuildRequires:	python-nose
BuildRequires:	python-pygpgme
BuildRequires:	python-rpm >= %{rpm_version}
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	sed >= 4.0
BuildRequires:	sphinx-pdg
BuildRequires:	systemd-devel
%if %{with tests}
BuildRequires:	hawkey-devel >= %{hawkey_version}
BuildRequires:	python-pyliblzma
%endif
Requires(post,preun,postun):	systemd-units >= 38
Requires:	deltarpm
Requires:	python-hawkey >= %{hawkey_version}
Requires:	python-iniparse
Requires:	python-libcomps >= %{libcomps_version}
Requires:	python-librepo >= %{librepo_version}
Requires:	python-pygpgme
Requires:	python-rpm >= %{rpm_version}
#Requires:	rpm-plugin-systemd-inhibit
Requires:	systemd-units >= 0.38
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Package manager forked from Yum, using libsolv as a dependency
resolver.

%package automatic
Summary:	Alternative CLI to "dnf upgrade" suitable for automatic, regular execution
Group:		Base
Requires:	%{name} = %{version}-%{release}
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd

%description automatic
Alternative CLI to "dnf upgrade" suitable for automatic, regular
execution.

%prep
%setup -q -n %{name}
%patch0 -p1

# the -D doesn't work
%{__sed} -i -e '/SYSTEMD_DIR/ s#/usr/lib/systemd/system#%{systemdunitdir}#' CMakeLists.txt

%build
%cmake \
	-DCMAKE_CXX_COMPILER_WORKS=1 -DCMAKE_CXX_COMPILER="%{__cc}" \
	-DPYTHON_DESIRED=2 \
	-DSYSTEMD_DIR=%{systemdunitdir} \
	.

%{__make}
%{__make} doc-man

%if %{with tests}
%{__make} ARGS="-V" test
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%find_lang %{name}

install -d $RPM_BUILD_ROOT{%{_sysconfdir}/%{name}/plugins,%{py_sitescriptdir}/dnf-plugins,%{_localstatedir}/log}
touch $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}{,-rpm,-plugin}.log

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post dnf-makecache.timer

%preun
%systemd_preun dnf-makecache.timer

%postun
%systemd_reload

%post automatic
%systemd_post dnf-automatic.timer

%preun automatic
%systemd_preun dnf-automatic.timer

%postun automatic
%systemd_reload

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%attr(755,root,root) %{_bindir}/dnf
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/plugins
%dir %{_sysconfdir}/%{name}/protected.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/dnf.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/protected.d/dnf.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/libreport/events.d/collect_dnf.conf
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%{_mandir}/man8/dnf.8*
%{_mandir}/man8/dnf.conf.8*
%{systemdunitdir}/dnf-makecache.service
%{systemdunitdir}/dnf-makecache.timer
%{py_sitescriptdir}/dnf
%exclude %{py_sitescriptdir}/dnf/automatic

%ghost %{_localstatedir}/log/%{name}.log
%ghost %{_localstatedir}/log/%{name}-rpm.log
%ghost %{_localstatedir}/log/%{name}-plugin.log
/etc/bash_completion.d/dnf-completion.bash

%files automatic
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dnf-automatic
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/automatic.conf
%{_mandir}/man8/dnf.automatic.8*
%{systemdunitdir}/dnf-automatic.service
%{systemdunitdir}/dnf-automatic.timer
%{py_sitescriptdir}/dnf/automatic
