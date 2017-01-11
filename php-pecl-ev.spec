# TODO
# - undo libev embedding (use system libev)

# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	ev
Summary:	Provides interface to libev library
Name:		%{php_name}-pecl-%{modname}
Version:	1.0.4
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	6670ad30d98a9b5a1bd5410285099689
URL:		https://pecl.php.net/package/ev/
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:5.4.0
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
%endif
%{?requires_php_extension}
Provides:	php(%{modname}) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ev provides interface to libev library - high performance
full-featured event loop written in C.

%prep
%setup -qc
mv %{modname}-%{version}/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
exec %{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="" \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

./run-tests.sh
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir}}
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir},%{_examplesdir}/%{name}-%{version}}

%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md TODO.md LICENSE CREDITS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
