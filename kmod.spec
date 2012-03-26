# TODO:
# - implement /etc/modprobe.d/kver/ support (just as in our module-init-tools)
# - modprobe keeps "-" in module names: sprunge.us/dYCZ (probably irrelevant)
%bcond_without	tests
Summary:	Linux kernel module handling
Summary(pl.UTF-8):	Obsługa modułów jądra Linuksa
Name:		kmod
Version:	7
Release:	4
License:	GPL v2+
Group:		Applications/System
Source0:	ftp://ftp.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
# Source0-md5:	7bd916ae1c8a38e7697fdd8118bc98eb
Source1:	%{name}-blacklist
Source2:	%{name}-usb
# http://git.kernel.org/?p=utils/kernel/kmod/kmod.git;a=patch;h=02629fa02e96763db7460a930239cc93649a52f8
Patch0:		%{name}-options.patch
URL:		http://git.kernel.org/?p=utils/kernel/kmod/kmod.git;a=summary
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake >= 1:1.11
BuildRequires:	gtk-doc >= 1.14
BuildRequires:	libtool >= 2:2.0
BuildRequires:	pkgconfig
BuildRequires:	xz-devel >= 1:4.99
BuildRequires:	zlib-devel
Requires:	%{name}-libs = %{version}-%{release}
# won't work on older kernels as these do not provide require information in /sys
Requires:	uname(release) >= 2.6.21
Provides:	virtual(module-tools)
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

%package libs-static
Summary:	Linux kernel module handling static library
Summary(pl.UTF-8):	Statyczna biblioteka do obsługi modułów jądra Linuksa
License:	LGPL v2.1+
Group:		Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description libs-static
Linux kernel module handling static library.

%description libs-static -l pl.UTF-8
Statyczna biblioteka do obsługi modułów jądra Linuksa.

%package devel
Summary:	Header files for %{name} library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki %{name}
License:	LGPL v2.1+
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%prep
%setup -q
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--enable-static \
	--disable-silent-rules \
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
	ln -s kmod $RPM_BUILD_ROOT%{_sbindir}/$prog
done

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libkmod.a $RPM_BUILD_ROOT%{_prefix}/%{_lib}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libkmod.la

:> $RPM_BUILD_ROOT/etc/modprobe.d/modprobe.conf

install %{SOURCE1} $RPM_BUILD_ROOT/etc/modprobe.d/blacklist.conf
install %{SOURCE2} $RPM_BUILD_ROOT/etc/modprobe.d/usb.conf

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
%{_mandir}/man5/modules.dep.bin.5*
%{_mandir}/man8/depmod.8*
%{_mandir}/man8/insmod.8*
%{_mandir}/man8/lsmod.8*
%{_mandir}/man8/modinfo.8*
%{_mandir}/man8/modprobe.8*
%{_mandir}/man8/rmmod.8*

%files libs
%defattr(644,root,root,755)
%doc libkmod/README
%attr(755,root,root) %{_libdir}/libkmod.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libkmod.so.2

%files libs-static
%defattr(644,root,root,755)
%{_prefix}/%{_lib}/libkmod.a

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libkmod.so
%{_includedir}/libkmod.h
%{_pkgconfigdir}/libkmod.pc
