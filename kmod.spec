# TODO
# - alias from /etc/modprobe.d/3.4.32.longterm-1/geninitrd.conf does not work for geninitrd
# - kmod no longer links with library dynamically since kmod-15:
#   kmod binary statically links to libkmod - if distro is only interested in
#   the kmod tool (for example in an initrd) it can refrain from installing the library
#
# Conditional build:
%bcond_without	openssl	# OpenSSL support for PKCS7 signatures in modinfo
%bcond_without	python3	# CPython 3.x module
%bcond_without	tests	# perform "make check" (init_module seems to require root for mkdir)

Summary:	Linux kernel module handling
Summary(pl.UTF-8):	Obsługa modułów jądra Linuksa
Name:		kmod
Version:	27
Release:	1
License:	GPL v2+
Group:		Applications/System
Source0:	https://www.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
# Source0-md5:	3973a74786670d3062d89a827e266581
Source1:	%{name}-blacklist
Source2:	%{name}-usb
Patch0:		%{name}-modprobe.d-kver.patch
Patch1:		%{name}-depmod.d-kver.patch
Patch2:		python-3.8.patch
URL:		https://git.kernel.org/pub/scm/utils/kernel/kmod/kmod.git
BuildRequires:	autoconf >= 2.64
BuildRequires:	automake >= 1:1.11
BuildRequires:	gtk-doc >= 1.14
BuildRequires:	kernel-module-build
BuildRequires:	libtool >= 2:2.0
%{?with_openssl:BuildRequires:	openssl-devel >= 1.1.0}
BuildRequires:	pkgconfig
BuildRequires:	python-devel >= 1:2.6
%{?with_python3:BuildRequires:	python3-devel >= 1:3.3}
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	xz-devel >= 1:4.99
BuildRequires:	zlib-devel
Requires:	filesystem >= 4.0-24
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
Summary:	Python 2 binding for kmod API
Summary(pl.UTF-8):	Wiązania Pythona 2 do API kmod
License:	LGPL v2.1+
Group:		Development/Languages/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python-kmod
Python 2 binding for kmod API.

%description -n python-kmod -l pl.UTF-8
Wiązania Pythona 2 do API kmod.

%package -n python3-kmod
Summary:	Python 3 binding for kmod API
Summary(pl.UTF-8):	Wiązania Pythona 3 do API kmod
License:	LGPL v2.1+
Group:		Development/Languages/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python3-kmod
Python 3 binding for kmod API.

%description -n python3-kmod -l pl.UTF-8
Wiązania Pythona 3 do API kmod.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}

install -d build
cd build
../%configure \
	--disable-silent-rules \
	--disable-test-modules \
	--enable-python \
	%{?with_openssl:--with-openssl} \
	--with-rootlibdir=/%{_lib} \
	--with-xz \
	--with-zlib
%{__make}
cd ..

%if %{with python3}
install -d build-py3
cd build-py3
../%configure \
	PYTHON=%{__python3} \
	--disable-silent-rules \
	--disable-test-modules \
	--enable-python \
	--with-rootlibdir=/%{_lib} \
	--with-xz \
	--with-zlib
%{__make}
cd ..
%endif

%if %{with tests}
%{__make} -C build check \
	KDIR=%{_kernelsrcdir} \
	KVER=%{_kernel_ver}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc,/lib}/{depmod.d,modprobe.d}

%if %{with python3}
%{__make} -C build-py3 install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%{__make} -C build install \
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
%if %{with python3}
%{__rm} $RPM_BUILD_ROOT%{py3_sitedir}/kmod/*.la
%endif

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
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/blacklist.conf
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/modprobe.conf
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/usb.conf

%dir /etc/depmod.d
%dir /lib/depmod.d
%dir /lib/modprobe.d

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

%if %{with python3}
%files -n python3-kmod
%defattr(644,root,root,755)
%dir %{py3_sitedir}/kmod
%attr(755,root,root) %{py3_sitedir}/kmod/*.so
%{py3_sitedir}/kmod/*.py
%{py3_sitedir}/kmod/__pycache__
%endif
