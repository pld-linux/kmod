# TODO
# - alias from /etc/modprobe.d/3.4.32.longterm-1/geninitrd.conf does not work for geninitrd
# - kmod no longer links with library dynamically since kmod-15:
#   kmod binary statically links to libkmod - if distro is only interested in
#   the kmod tool (for example in an initrd) it can refrain from installing the library
#
# Conditional build:
%bcond_without	tests	# perform "make check" (init_module seems to require root for mkdir)

Summary:	Linux kernel module handling
Summary(pl.UTF-8):	Obsługa modułów jądra Linuksa
Name:		kmod
Version:	19
Release:	1
License:	GPL v2+
Group:		Applications/System
Source0:	https://www.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
# Source0-md5:	a08643f814aa4efc12211c6e5909f4d9
Source1:	%{name}-blacklist
Source2:	%{name}-usb
Patch0:		%{name}-modprobe.d-kver.patch
URL:		http://git.kernel.org/?p=utils/kernel/kmod/kmod.git;a=summary
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake >= 1:1.11
BuildRequires:	gtk-doc >= 1.14
BuildRequires:	libtool >= 2:2.0
BuildRequires:	pkgconfig
BuildRequires:	python-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	xz-devel >= 1:4.99
BuildRequires:	zlib-devel
# won't work on older kernels as these do not provide require information in /sys
Requires:	uname(release) >= 2.6.21
Provides:	module-init-tools = 4.0
Provides:	virtual(module-tools)
Obsoletes:	module-init-tools < 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_bindir		/sbin

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

%package libs
Summary:	Linux kernel module handling library
Summary(pl.UTF-8):	Biblioteka do obsługi modułów jądra Linuksa
License:	LGPL v2.1+
Group:		Libraries
Conflicts:	kmod < 4-1

%description libs
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%description libs -l pl.UTF-8
Biblioteka libkmod została zaprojektowana, aby pozwolić programom w
łatwy sposób ładować, usuwać i listować moduły, także sprawdzając ich
właściwości, zależności i aliasy.

%package devel
Summary:	Header files for %{name} library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki %{name}
License:	LGPL v2.1+
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Obsoletes:	kmod-libs-static

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%package -n bash-completion-kmod
Summary:	bash-completion for kmod utilities
Summary(pl.UTF-8):	Bashowe uzupełnianie nazw dla narzędzi kmod
Group:		Applications/Shells
Requires:	bash-completion >= 2.0
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-kmod
bash-completion for kmod utilities.

%description -n bash-completion-kmod -l pl.UTF-8
Bashowe uzupełnianie nazw dla narzędzi kmod.

%package -n python-kmod
Summary:	Python binding for kmod API
Summary(pl.UTF-8):	Wiązania Pythona do API kmod
License:	LGPL v2.1+
Group:		Development/Languages/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python-kmod
Python binding for kmod API.

%description -n python-kmod -l pl.UTF-8
Wiązania Pythona do API kmod.

%prep
%setup -q
%patch0 -p1

# requires root to work
sed -i -e 's# testsuite/test-modprobe # #g' Makefile.am

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	--enable-python \
	--with-rootlibdir=/%{_lib} \
	--with-xz \
	--with-zlib
%{__make}

%{?with_tests:%{__make} check}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/modprobe.d
%{__make} install \
	pkgconfigdir=%{_pkgconfigdir} \
	DESTDIR=$RPM_BUILD_ROOT

# install symlinks
for prog in lsmod rmmod insmod modinfo modprobe depmod; do
	ln -s kmod $RPM_BUILD_ROOT%{_bindir}/$prog
done

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libkmod.la

# not needed in python module
%{__rm} $RPM_BUILD_ROOT%{py_sitedir}/kmod/*.la
%py_postclean

:> $RPM_BUILD_ROOT/etc/modprobe.d/modprobe.conf

cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/modprobe.d/blacklist.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/modprobe.d/usb.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README TODO
%dir /etc/modprobe.d
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/blacklist.conf
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/modprobe.conf
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/usb.conf

%attr(755,root,root) %{_bindir}/kmod
%attr(755,root,root) %{_bindir}/lsmod
%attr(755,root,root) %{_bindir}/rmmod
%attr(755,root,root) %{_bindir}/insmod
%attr(755,root,root) %{_bindir}/modinfo
%attr(755,root,root) %{_bindir}/modprobe
%attr(755,root,root) %{_bindir}/depmod

%{_mandir}/man5/depmod.d.5*
%{_mandir}/man5/modprobe.d.5*
%{_mandir}/man5/modules.dep.5*
%{_mandir}/man5/modules.dep.bin.5*
%{_mandir}/man8/depmod.8*
%{_mandir}/man8/insmod.8*
%{_mandir}/man8/kmod.8*
%{_mandir}/man8/lsmod.8*
%{_mandir}/man8/modinfo.8*
%{_mandir}/man8/modprobe.8*
%{_mandir}/man8/rmmod.8*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/libkmod.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libkmod.so.2

%files devel
%defattr(644,root,root,755)
%doc libkmod/README
%attr(755,root,root) %{_libdir}/libkmod.so
%{_includedir}/libkmod.h
%{_pkgconfigdir}/libkmod.pc

%files -n bash-completion-kmod
%defattr(644,root,root,755)
%{_datadir}/bash-completion/completions/kmod

%files -n python-kmod
%defattr(644,root,root,755)
%dir %{py_sitedir}/kmod
%attr(755,root,root) %{py_sitedir}/kmod/*.so
%{py_sitedir}/kmod/*.py[co]
