# TODO
# - make -DSYSTEMD_DIR actually to work: https://github.com/rpm-software-management/dnf/pull/213
#
# Conditional build:
%bcond_without	tests		# build without tests
%bcond_without	python2		# CPython 2.x version
%bcond_with	python3		# CPython 3.x version (dependencies not met currently)
#
%define	gitrev	a7e0aa1
%define	hawkey_ver	0.5.2
%define	librepo_ver	1.7.5
%define	libcomps_ver	0.1.6
%define	rpm_ver		5.4.0

Summary:	Package manager forked from Yum, using libsolv as a dependency resolver
Summary(pl.UTF-8):	Zarządca pakietów wywodzący się z Yuma, wykorzystujący libsolv do rozwiązywania zależności
Name:		dnf
Version:	0.6.3
Release:	0.5
Group:		Base
# GPL v2+ with GPL v2 and GPL parts; for a breakdown of the licensing, see PACKAGE-LICENSING
License:	GPL v2 (parts on GPL v2+ or GPL)
#Source0:	http://rpm-software-management.fedorapeople.org/%{name}-%{gitrev}.tar.xz
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/dnf/%{name}-%{gitrev}.tar.xz/82ff495e445ddc56e70dc91750a421ac/dnf-%{gitrev}.tar.xz
# Source0-md5:	82ff495e445ddc56e70dc91750a421ac
Patch0:		rpm5.patch
URL:		https://github.com/rpm-software-management/dnf
BuildRequires:	cmake >= 2.4
BuildRequires:	gettext-tools
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	sed >= 4.0
BuildRequires:	sphinx-pdg
BuildRequires:	systemd-devel
%if %{with python2}
BuildRequires:	python >= 2
%if %{with tests}
#BuildRequires:	python-bugzilla
BuildRequires:	python-hawkey >= %{hawkey_ver}
BuildRequires:	python-hawkey-test >= %{hawkey_ver}
BuildRequires:	python-iniparse
BuildRequires:	python-libcomps >= %{libcomps_ver}
BuildRequires:	python-librepo >= %{librepo_ver}
BuildRequires:	python-pygpgme
BuildRequires:	python-rpm >= %{rpm_ver}
BuildRequires:	python-nose
BuildRequires:	python-pyliblzma
%endif
%endif
%if %{with python3}
BuildRequires:	python3 >= 1:3.3
%endif
Requires(post,preun,postun):	systemd-units >= 38
Requires:	deltarpm
Requires:	python-hawkey >= %{hawkey_ver}
Requires:	python-iniparse
Requires:	python-libcomps >= %{libcomps_ver}
Requires:	python-librepo >= %{librepo_ver}
Requires:	python-pygpgme
Requires:	python-rpm >= %{rpm_ver}
#Requires:	rpm-plugin-systemd-inhibit
Requires:	systemd-units >= 0.38
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Package manager forked from Yum, using libsolv as a dependency
resolver.

%description -l pl.UTF-8
Zarządca pakietów wywodzący się z Yuma, wykorzystujący libsolv do
rozwiązywania zależności.

%package automatic
Summary:	Alternative CLI to "dnf upgrade" suitable for automatic, regular execution
Summary(pl.UTF-8):	Alternatywny interfejs do "dnf upgrade" nadający się do automatycznego wywoływania
Group:		Base
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires:	%{name} = %{version}-%{release}

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

%description -n bash-completion-dnf
Bash completion for dnf command.

%description -n bash-completion-dnf -l pl.UTF-8
Bashowe uzupełnianie parametrów dla polecenia dnf.

%package -n python3-dnf
Summary:	Python 3 version of dnf package manager
Summary(pl.UTF-8):	Wersja zarządcy pakietów dnf dla Pythona 3
Group:		Libraries/Python
# for common files (make -common?)
Requires:	%{name} = %{version}-%{release}
Requires:	deltarpm
Requires:	python3-hawkey >= %{hawkey_ver}
# XXX: missing in PLD
#Requires:	python3-iniparse
Requires:	python3-libcomps >= %{libcomps_ver}
# XXX: missing in PLD
#Requires:	python3-librepo >= %{librepo_ver}
Requires:	python3-pygpgme
# XXX: missing in PLD (is it possible with rpm5?)
#Requires:	python3-rpm >= %{rpm_ver}

%description -n python3-dnf
Python 3 version of dnf package manager.

%description -n python3-dnf -l pl.UTF-8
Wersja zarządcy pakietów dnf dla Pythona 3.

%prep
%setup -q -n %{name}
%patch0 -p1

# the -D doesn't work
%{__sed} -i -e '/SYSTEMD_DIR/ s#/usr/lib/systemd/system#%{systemdunitdir}#' CMakeLists.txt

%build
%if %{with python2}
install -d build-py2
cd build-py2
%cmake .. \
	-DCMAKE_CXX_COMPILER="%{__cc}" \
	-DCMAKE_CXX_COMPILER_WORKS=1 \
	-DPYTHON_DESIRED=2 \
	-DSYSTEMD_DIR=%{systemdunitdir}

%{__make}
%{__make} doc-man

%if %{with tests}
%{__make} test ARGS="-V"
%endif

cd ..
%endif

%if %{with python3}
install -d build-py3
cd build-py3
%cmake .. \
	-DCMAKE_CXX_COMPILER="%{__cc}" \
	-DCMAKE_CXX_COMPILER_WORKS=1 \
	-DPYTHON_DESIRED=3 \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DSYSTEMD_DIR=%{systemdunitdir}

%{__make}
%{__make} doc-man
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with python2}
%{__make} -C build-py2 install \
	DESTDIR=$RPM_BUILD_ROOT

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%find_lang %{name}

install -d $RPM_BUILD_ROOT{%{_sysconfdir}/%{name}/plugins,%{py_sitescriptdir}/dnf-plugins,%{_localstatedir}/log}
touch $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}{,-rpm,-plugin}.log
%endif

%if %{with python3}
%{__make} -C build-py3 install \
	DESTDIR=$RPM_BUILD_ROOT

%py3_ocomp $RPM_BUILD_ROOT%{py3_sitescriptdir}
%py3_comp $RPM_BUILD_ROOT%{py3_sitescriptdir}
%else
%{__rm} $RPM_BUILD_ROOT%{_bindir}/dnf-3
%endif

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

%if %{with python2}
%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS PACKAGE-LICENSING README.rst
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

%files automatic
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dnf-automatic
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/automatic.conf
%{_mandir}/man8/dnf.automatic.8*
%{systemdunitdir}/dnf-automatic.service
%{systemdunitdir}/dnf-automatic.timer
%{py_sitescriptdir}/dnf/automatic
%endif

%files -n bash-completion-dnf
%defattr(644,root,root,755)
/etc/bash_completion.d/dnf-completion.bash

%if %{with python3}
%files -n python3-dnf
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/dnf-3
%{py3_sitescriptdir}/dnf
%endif
