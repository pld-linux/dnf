#
# Conditional build:
%bcond_without	tests		# build without tests
#
%define		hawkey_ver		0.67.0
%define		libcomps_ver		0.1.8
%define		libmodulemd_ver		2.9.3
%define		rpm_ver			4.14.0

%define		_enable_debug_packages	0

Summary:	Package manager
Summary(pl.UTF-8):	Zarządca pakietów
Name:		dnf
Version:	4.12.0
Release:	2
Group:		Base
# GPL v2+ with GPL v2 and GPL parts; for a breakdown of the licensing, see PACKAGE-LICENSING
License:	GPL v2 (parts on GPL v2+ or GPL)
Source0:	https://github.com/rpm-software-management/dnf/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	0e0242e443f87290efd16226b056f18c
Source1:	pld.repo
Source2:	pld-archive.repo
Source3:	pld-debuginfo.repo
Source4:	pld-multilib.repo
Patch0:		install.patch
Patch1:		repos.d.patch
Patch2:		uname-cpuinfo-deps.patch
URL:		https://github.com/rpm-software-management/dnf
BuildRequires:	bash-completion-devel
BuildRequires:	cmake >= 2.4
BuildRequires:	gettext-tools
BuildRequires:	libmodulemd >= %{libmodulemd_ver}
BuildRequires:	python3
BuildRequires:	python3-gpg
BuildRequires:	python3-hawkey >= %{hawkey_ver}
BuildRequires:	python3-libcomps >= %{libcomps_ver}
BuildRequires:	python3-libdnf >= %{hawkey_ver}
BuildRequires:	python3-modules
BuildRequires:	python3-nose
BuildRequires:	python3-rpm >= %{rpm_ver}
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	rpm-pythonprov
BuildRequires:	sed >= 4.0
BuildRequires:	sphinx-pdg
BuildRequires:	systemd-devel
Requires(post,preun,postun):	systemd-units >= 38
Requires:	libmodulemd >= %{libmodulemd_ver}
Requires:	python3-gpg
Requires:	python3-hawkey >= %{hawkey_ver}
Requires:	python3-libcomps >= %{libcomps_ver}
Requires:	python3-libdnf >= %{hawkey_ver}
Requires:	python3-modules
Requires:	python3-rpm
Requires:	systemd-units >= 0.38
Recommends:	deltarpm
Recommends:	python3-dbus
Recommends:	python3-unbound
Recommends:	rpm-plugin-systemd-inhibit
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Utility that allows users to manage packages on their systems. It
supports RPMs, modules and comps groups & environments.

%description -l pl.UTF-8
Marzędzie umożliwiające użytkownikom zarządzanie pakietami w systemie.

%package automatic
Summary:	Alternative CLI to "dnf upgrade" suitable for automatic, regular execution
Summary(pl.UTF-8):	Alternatywny interfejs do "dnf upgrade" nadający się do automatycznego wywoływania
Group:		Base
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires:	%{name} = %{version}-%{release}
Requires:	python3-modules
BuildArch:	noarch

%description automatic
Alternative CLI to "dnf upgrade" suitable for automatic, regular
execution.

%description automatic -l pl.UTF-8
Alternatywny interfejs linii poleceń do "dnf upgrade", nadający się do
automatycznego, regularnego wywoływania.

%package -n bash-completion-dnf
Summary:	Bash completion for dnf command
Summary(pl.UTF-8):	Bashowe uzupełnianie parametrów dla polecenia dnf
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion
BuildArch:	noarch

%description -n bash-completion-dnf
Bash completion for dnf command.

%description -n bash-completion-dnf -l pl.UTF-8
Bashowe uzupełnianie parametrów dla polecenia dnf.

%package -n yum
Summary:	Yum compatibility layer for DNF
Summary(pl.UTF-8):	Warstwa zgodności z YUM-em dla DNF-a
Group:		Base
Requires:	%{name} = %{version}-%{release}
Recommends:	sqlite3
Conflicts:	yum < 3.4.3-505
BuildArch:	noarch

%description -n yum
Yum compatibility layer for DNF.

%description -n yum -l pl.UTF-8
Warstwa zgodności z YUM-em dla DNF-a.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
install -d build
cd build
%cmake .. \
	-DPYTHON_DESIRED:FILEPATH=%{__python3} \
	-DPYTHON_INSTALL_DIR:PATH=%{py3_sitescriptdir} \
	-DDNF_VERSION=%{version} \
	-DSYSTEMD_DIR=%{systemdunitdir}

%{__make}
%{__make} doc-man

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{yum,%{name}/{vars,aliases.d,plugins,modules.d,modules.defaults.d,repos.d}} \
	-d $RPM_BUILD_ROOT{%{_localstatedir}/log/,%{_var}/cache/dnf} \
	-d $RPM_BUILD_ROOT%{py3_sitescriptdir}/dnf-plugins/__pycache__

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

touch $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}.log

%{__mv} $RPM_BUILD_ROOT%{_bindir}/dnf-3 $RPM_BUILD_ROOT%{_bindir}/dnf
%{__mv} $RPM_BUILD_ROOT%{_bindir}/dnf-automatic-3 $RPM_BUILD_ROOT%{_bindir}/dnf-automatic

%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/{%{name}-strict.conf,aliases.d/zypper.conf}

# YUM compat layer
ln -sr $RPM_BUILD_ROOT%{_sysconfdir}/{%{name}/%{name}.conf,yum.conf}
ln -sr $RPM_BUILD_ROOT%{_sysconfdir}/{%{name}/plugins,yum/pluginconf.d}
ln -sr $RPM_BUILD_ROOT%{_sysconfdir}/{%{name}/protected.d,yum/protected.d}
ln -sr $RPM_BUILD_ROOT%{_sysconfdir}/{%{name}/repos.d,yum/repos.d}
ln -sr $RPM_BUILD_ROOT%{_sysconfdir}/{%{name}/vars,yum/vars}
ln -s dnf $RPM_BUILD_ROOT%{_bindir}/yum

%ifarch i686 ppc sparc alpha athlon aarch64 %{arm}
	%define		ftp_arch	%{_target_cpu}
%endif
%ifarch pentium2 pentium3 pentium4
	%define		ftp_arch	i686
%endif
%ifarch %{x8664}
	%define		ftp_arch	x86_64
	%define		ftp_alt_arch	i686
	%define		ftp_alt2_arch	x32
%endif
%ifarch x32
	%define		ftp_arch	x32
	%define		ftp_alt_arch	x86_64
	%define		ftp_alt2_arch	i686
%endif

%define	pld_repo %{SOURCE1}
%define	pld_archive_repo %{SOURCE2}
%define	pld_debuginfo_repo %{SOURCE3}

%ifarch %{x8664} x32
	%define	pld_multilib_repo %{SOURCE4}
	%define	pld_multilib2_repo %{SOURCE4}
%endif

%{__sed} -e 's|%%ARCH%%|%{ftp_arch}|g' < %{pld_repo} > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/repos.d/pld.repo

%if 0%{?pld_multilib_repo:1}
	%{__sed} 's|%%ARCH%%|%{ftp_alt_arch}|g' < %{pld_multilib_repo} > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/repos.d/pld-%{ftp_alt_arch}.repo
%endif

%if 0%{?pld_multilib2_repo:1}
	%{__sed} 's|%%ARCH%%|%{ftp_alt2_arch}|g' < %{pld_multilib_repo} > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/repos.d/pld-%{ftp_alt2_arch}.repo
%endif

%if 0%{?pld_debuginfo_repo:1}
%{__sed} -e 's|%%ARCH%%|%{ftp_arch}|g' < %{pld_debuginfo_repo} > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/repos.d/pld-debuginfo.repo
%endif

%if 0%{?pld_archive_repo:1}
%{__sed} -e 's|%%ARCH%%|%{ftp_arch}|g' < %{pld_archive_repo} > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/repos.d/pld-archive.repo
%endif

%py3_comp $RPM_BUILD_ROOT%{py3_sitescriptdir}/dnf
%py3_ocomp $RPM_BUILD_ROOT%{py3_sitescriptdir}/dnf

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post dnf-makecache.timer

%preun
%systemd_preun dnf-makecache.timer

%postun
%systemd_reload

%post automatic
%systemd_post dnf-automatic.timer dnf-automatic-download.timer dnf-automatic-install.timer dnf-automatic-notifyonly.timer

%preun automatic
%systemd_preun dnf-automatic.timer dnf-automatic-download.timer dnf-automatic-install.timer dnf-automatic-notifyonly.timer

%postun automatic
%systemd_reload

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS PACKAGE-LICENSING README.rst
%attr(755,root,root) %{_bindir}/dnf
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/plugins
%dir %{_sysconfdir}/%{name}/protected.d
%dir %{_sysconfdir}/%{name}/repos.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/dnf.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/protected.d/dnf.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/repos.d/*.repo
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/libreport/events.d/collect_dnf.conf
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%{_mandir}/man5/dnf.conf.5*
%{_mandir}/man5/dnf-transaction-json.5*
%{_mandir}/man7/dnf.modularity.7*
%{_mandir}/man8/dnf.8*
%{_mandir}/man8/yum2dnf.8*
%{systemdunitdir}/dnf-makecache.service
%{systemdunitdir}/dnf-makecache.timer
%{systemdtmpfilesdir}/dnf.conf
%{py3_sitescriptdir}/dnf
%{py3_sitescriptdir}/dnf-plugins
%exclude %{py3_sitescriptdir}/dnf/automatic
%dir %{_var}/cache/dnf
%ghost %{_localstatedir}/log/%{name}.log

%files automatic
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dnf-automatic
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/automatic.conf
%{_mandir}/man8/dnf-automatic.8*
%{systemdunitdir}/dnf-automatic-download.service
%{systemdunitdir}/dnf-automatic-download.timer
%{systemdunitdir}/dnf-automatic-install.service
%{systemdunitdir}/dnf-automatic-install.timer
%{systemdunitdir}/dnf-automatic-notifyonly.service
%{systemdunitdir}/dnf-automatic-notifyonly.timer
%{systemdunitdir}/dnf-automatic.service
%{systemdunitdir}/dnf-automatic.timer
%{py3_sitescriptdir}/dnf/automatic

%files -n bash-completion-dnf
%defattr(644,root,root,755)
%{bash_compdir}/dnf

%files -n yum
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/yum
%{_sysconfdir}/yum.conf
%dir %{_sysconfdir}/yum
%{_sysconfdir}/yum/pluginconf.d
%{_sysconfdir}/yum/protected.d
%{_sysconfdir}/yum/repos.d
%{_sysconfdir}/yum/vars
%{_mandir}/man1/yum-aliases.1*
%{_mandir}/man5/yum.conf.5.*
%{_mandir}/man8/yum.8*
%{_mandir}/man8/yum-shell.8*
%config(noreplace) %{_sysconfdir}/%{name}/protected.d/yum.conf
