# TODO
# - alias from /etc/modprobe.d/3.4.32.longterm-1/geninitrd.conf does not work for geninitrd
# - kmod no longer links with library dynamically since kmod-15:
#   kmod binary statically links to libkmod - if distro is only interested in
#   the kmod tool (for example in an initrd) it can refrain from installing the library
#
# Conditional build:
%bcond_without	openssl	# OpenSSL support for PKCS7 signatures in modinfo
%bcond_with	apidocs	# gtk-doc based API documentation (currently disabled by empty gtk-doc.make file)
%bcond_without	tests	# perform "make check" (init_module seems to require root for mkdir)

Summary:	Linux kernel module handling
Summary(pl.UTF-8):	Obsługa modułów jądra Linuksa
Name:		kmod
Version:	34.2
Release:	1
License:	GPL v2+
Group:		Applications/System
Source0:	https://www.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
# Source0-md5:	36f2cc483745e81ede3406fa55e1065a
Source1:	%{name}-blacklist
Source2:	%{name}-usb
Patch0:		%{name}-modprobe.d-kver.patch
Patch1:		%{name}-depmod.d-kver.patch
Patch2:		xz-in-kernel-decompr-compat.patch
URL:		https://git.kernel.org/pub/scm/utils/kernel/kmod/kmod.git
BuildRequires:	autoconf >= 2.64
BuildRequires:	automake >= 1:1.11
BuildRequires:	bash-completion-devel >= 1:2.0
%{?with_apidocs:BuildRequires:	gtk-doc >= 1.14}
%if %{with tests}
BuildRequires:	kernel-module-build
%endif
BuildRequires:	libtool >= 2:2.0
%{?with_openssl:BuildRequires:	openssl-devel >= 1.1.0}
BuildRequires:	pkgconfig
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.752
BuildRequires:	scdoc
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	xz-devel >= 1:4.99
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel >= 1.4.4
Requires:	filesystem >= 4.0-24
# won't work on older kernels as these do not provide require information in /sys
Requires:	uname(release) >= 2.6.21
Requires:	zstd >= 1.4.4
Provides:	module-init-tools = 4.0
Provides:	virtual(module-tools)
Obsoletes:	bash-completion-kmod < 34.2
Obsoletes:	module-init-tools < 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_bindir		/sbin
%define		_sbindir	/sbin
%define		_slibdir	/%{_lib}
%define		bash_compdir	%(pkg-config --variable compatdir bash-completion 2> /dev/null || echo ERROR)

%define		filterout_cpp	-DNDEBUG

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
Requires:	zstd >= 1.4.4
Obsoletes:	python-kmod < 32
Obsoletes:	python3-kmod < 32
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
Obsoletes:	kmod-libs-static < 14

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%prep
%setup -q
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	%{?with_apidocs:--enable-gtk-doc} \
	%{?with_python2:--enable-python} \
	--with-distconfdir=/%{_lib} \
	--with-bashcompletiondir=%{bash_compdir} \
	--with-fishcompletiondir=%{fish_compdir} \
	--with-zshcompletiondir=%{zsh_compdir} \
	%{?with_openssl:--with-openssl} \
	--with-xz \
	--with-zlib \
	--with-zstd
%{__make}

%if %{with tests}
%{__make} check \
	KDIR=%{_kernelsrcdir} \
	KVER=%{_kernel_ver} \
	MAKEFLAGS=CONFIG_RANDSTRUCT=n
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc,/lib}/{depmod.d,modprobe.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_slibdir}
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libkmod.so.* $RPM_BUILD_ROOT%{_slibdir}
ln -sf --relative $RPM_BUILD_ROOT%{_slibdir}/libkmod.so.*.*.* $RPM_BUILD_ROOT%{_libdir}/libkmod.so

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libkmod.la

:> $RPM_BUILD_ROOT/etc/modprobe.d/modprobe.conf

cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/modprobe.d/blacklist.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/modprobe.d/usb.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README.md
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/blacklist.conf
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/modprobe.conf
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/usb.conf

%dir /etc/depmod.d
%dir /lib/depmod.d
%dir /lib/modprobe.d

%attr(755,root,root) %{_bindir}/kmod
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
%{_mandir}/man8/kmod.8*
%{_mandir}/man8/lsmod.8*
%{_mandir}/man8/modinfo.8*
%{_mandir}/man8/modprobe.8*
%{_mandir}/man8/rmmod.8*

%{bash_compdir}/insmod
%{bash_compdir}/kmod
%{bash_compdir}/lsmod
%{bash_compdir}/rmmod

%{fish_compdir}/insmod.fish
%{fish_compdir}/lsmod.fish
%{fish_compdir}/rmmod.fish

%{zsh_compdir}/_insmod
%{zsh_compdir}/_lsmod
%{zsh_compdir}/_rmmod

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_slibdir}/libkmod.so.*.*.*
%ghost %{_slibdir}/libkmod.so.2

%files devel
%defattr(644,root,root,755)
%doc libkmod/README
%{_libdir}/libkmod.so
%{_includedir}/libkmod.h
%{_pkgconfigdir}/libkmod.pc
%{_npkgconfigdir}/kmod.pc
