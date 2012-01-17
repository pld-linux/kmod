Summary:	Linux kernel module handling
Summary(pl.UTF-8):	Obsługa modułów jądra Linuksa
Name:		kmod
Version:	4
Release:	1
License:	GPL v2
Group:		Applications/System
Source0:	http://packages.profusion.mobi/kmod/%{name}-%{version}.tar.xz
# Source0-md5:	e14450a066a48accd0af1995b3c0232d
URL:		http://git.profusion.mobi/cgit.cgi/kmod.git/
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake >= 1:1.11
BuildRequires:	libtool >= 2:2.0
BuildRequires:	xz-devel >= 1:4.99
BuildRequires:	zlib-devel
# won't work on older kernels as these do not provide require information in /sys
Requires:	uname(release) >= 2.6.21
Obsoletes:	module-init-tools
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_exec_prefix	/
%define		_bindir		%{_sbindir}

%description
kmod is a set of tools to handle common tasks with Linux kernel
modules like insert, remove, list, check properties, resolve
dependencies and aliases.

These tools are designed on top of libkmod, a library that is shipped
with kmod. See libkmod/README for more details on this library and how
to use it. The aim is to be compatible with tools, configurations and
indexes from module-init-tools project.

%description -l pl.UTF-8
kmod to zestaw narzędzi do wykonywania typowych czynności związanych z
modułami jądra - ładowanie, usuwanie, listowanie, sprawdzanie
parametrów, rozwiązywanie zależności czy obsługa aliasów.

Narzędzia te zostały stworzone przy użyciu libkmod, biblioteki
dostarczanej wraz z kmod. Celem jest stworzenie narzędzi
kompatybilnych z programami, konfiguracją oraz indeksami z projektu
module-init-tools.

%package devel
Summary:	Header files for %{name} library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%prep
%setup -q

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	--with-xz \
	--with-zlib
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	pkgconfigdir=%{_pkgconfigdir} \
	DESTDIR=$RPM_BUILD_ROOT

# install symlinks
for prog in lsmod rmmod insmod modinfo modprobe depmod; do
	ln -s kmod $RPM_BUILD_ROOT%{_sbindir}/$prog
done

%{__rm} $RPM_BUILD_ROOT%{_libdir}/libkmod.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README TODO
%attr(755,root,root) %{_libdir}/libkmod.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libkmod.so.1
%attr(755,root,root) %{_sbindir}/kmod
%attr(755,root,root) %{_sbindir}/lsmod
%attr(755,root,root) %{_sbindir}/rmmod
%attr(755,root,root) %{_sbindir}/insmod
%attr(755,root,root) %{_sbindir}/modinfo
%attr(755,root,root) %{_sbindir}/modprobe
%attr(755,root,root) %{_sbindir}/depmod

%{_mandir}/man5/depmod.d.5*
%{_mandir}/man5/modprobe.d.5*
%{_mandir}/man5/modules.dep.5*
%{_mandir}/man8/depmod.8*
%{_mandir}/man8/insmod.8*
%{_mandir}/man8/lsmod.8*
%{_mandir}/man8/modinfo.8*
%{_mandir}/man8/modprobe.8*
%{_mandir}/man8/rmmod.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libkmod.so
%{_includedir}/libkmod.h
%{_pkgconfigdir}/libkmod.pc
