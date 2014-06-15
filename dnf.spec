# TODO
# - bash-completion subpackage
# - make -DSYSTEMD_DIR actually to work
%define	gitrev c44cc44
%define	hawkey_version 0.4.14
%define	librepo_version 1.7.0
%define	libcomps_version 0.1.6
Summary:	Package manager forked from Yum, using libsolv as a dependency resolver
Name:		dnf
Version:	0.5.1
Release:	0.5
Group:		Base
# For a breakdown of the licensing, see PACKAGE-LICENSING
License:	GPL v2+ and GPL v2 and GPL
#Source0:	http://akozumpl.fedorapeople.org/%{name}-%{gitrev}.tar.xz
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/dnf/%{name}-%{gitrev}.tar.xz/fdf85937f979702e1968150e8e150666/dnf-%{gitrev}.tar.xz
# Source0-md5:	fdf85937f979702e1968150e8e150666
Patch0:		rpm5.patch
URL:		https://github.com/akozumpl/dnf
BuildRequires:	cmake
BuildRequires:	gettext
BuildRequires:	python
BuildRequires:	python-Sphinx
#BuildRequires:	python-bugzilla
BuildRequires:	python-hawkey >= %{hawkey_version}
BuildRequires:	python-iniparse
BuildRequires:	python-libcomps >= %{libcomps_version}
BuildRequires:	python-librepo >= %{librepo_version}
BuildRequires:	python-nose
BuildRequires:	python-rpm
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	sed >= 4.0
BuildRequires:	sphinx-pdg
BuildRequires:	systemd-devel
Requires(post,preun,postun):	systemd-units >= 38
Requires:	deltarpm
Requires:	python-hawkey >= %{hawkey_version}
Requires:	python-iniparse
Requires:	python-libcomps >= %{libcomps_version}
Requires:	python-librepo >= %{librepo_version}
Requires:	python-rpm
Requires:	systemd-units >= 0.38
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Package manager forked from Yum, using libsolv as a dependency
resolver.

%prep
%setup -q -n %{name}
%patch0 -p1

# the -D doesn't work
%{__sed} -i -e '/SYSTEMD_DIR/ s#/usr/lib/systemd/system#%{systemdunitdir}#' CMakeLists.txt

%build
%cmake \
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

mv $RPM_BUILD_ROOT%{_localedir}/lt{_LT,}
rm -r $RPM_BUILD_ROOT%{_localedir}/id_ID
%find_lang %{name}

install -d $RPM_BUILD_ROOT{%{py_sitescriptdir}/dnf-plugins,%{_localstatedir}/log}
touch $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}.log

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post dnf-makecache.timer

%preun
%systemd_preun dnf-makecache.timer

%postun
%systemd_reload

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%attr(755,root,root) %{_bindir}/dnf
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/dnf.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/libreport/events.d/collect_dnf.conf
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%{_mandir}/man8/dnf.8*
%{_mandir}/man8/dnf.conf.8*
%{systemdunitdir}/dnf-makecache.service
%{systemdunitdir}/dnf-makecache.timer
%{py_sitescriptdir}/dnf
%{py_sitescriptdir}/dnf-plugins

%ghost %{_localstatedir}/log/%{name}.log
/etc/bash_completion.d/dnf-completion.bash
