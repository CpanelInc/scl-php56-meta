# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix %{ns_dir}
%global scl_name_base    %{ns_name}-php
%global scl_macro_base   %{ns_name}_php
%global scl_name_version 56
%global scl              %{scl_name_base}%{scl_name_version}
%scl_package %scl

Summary:       Package that installs PHP 5.6
Name:          %scl_name
Version:       5.6.40
Vendor:        cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4586 for more details
%define release_prefix 7
Release: %{release_prefix}%{?dist}.cpanel
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README
Source2:       LICENSE
Source3:       whm_feature_addon

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common
Requires:      %{?scl_prefix}php-cli

# Our code requires that pear be installed when the meta package is installed
Requires:      %{?scl_prefix}pear

%description
This is the main package for %scl Software Collection,
that install PHP 5.6 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.


%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

Provides:  ea-php-scldevel = %{version}
Conflicts: ea-php-scldevel > %{version}, ea-php-scldevel < %{version}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_macro_base}         %{scl}
%%scl_prefix_%{scl_macro_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/etc
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/share/doc
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/include
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/share/man/man1
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/bin
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/var/cache
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/var/tmp
mkdir -p %{buildroot}/opt/cpanel/ea-php56/root/usr/%{_lib}
mkdir -p %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures
install %{SOURCE3} %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures/%{name}

# Even if this package doesn't use it we need to do this because if another
# package does (e.g. pear licenses) it will be created and unowned by any RPM
%if 0%{?_licensedir:1}
mkdir %{buildroot}/%{_licensedir}
%endif

%scl_install

tmp_version=$(echo %{scl_name_version} | sed -re 's/([0-9])([0-9])/\1\.\2/')
sed -e 's/@SCL@/%{scl_macro_base}%{scl_name_version}/g' -e "s/@VERSION@/${tmp_version}/g" %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Remove empty share/[man|locale]/ directories
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/man/ -type d -empty -delete
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale/ -type d -empty -delete
mkdir -p %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files


%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*
%dir /opt/cpanel/ea-php56/root/etc
%dir /opt/cpanel/ea-php56/root/usr
%dir /opt/cpanel/ea-php56/root/usr/share
%dir /opt/cpanel/ea-php56/root/usr/share/doc
%dir /opt/cpanel/ea-php56/root/usr/include
%dir /opt/cpanel/ea-php56/root/usr/share/man
%dir /opt/cpanel/ea-php56/root/usr/bin
%dir /opt/cpanel/ea-php56/root/usr/var
%dir /opt/cpanel/ea-php56/root/usr/var/cache
%dir /opt/cpanel/ea-php56/root/usr/var/tmp
%dir /opt/cpanel/ea-php56/root/usr/%{_lib}
%attr(644, root, root) /usr/local/cpanel/whostmgr/addonfeatures/%{name}
%if 0%{?_licensedir:1}
%dir %{_licensedir}
%endif

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel


%changelog
* Wed May 10 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 5.6.40-7
- ZC-10936: Clean up Makefile and remove debug-package-nil

* Tue Dec 28 2021 Dan Muey <dan@cpanel.net> - 5.6.40-6
- ZC-9589: Update DISABLE_BUILD to match OBS

* Mon Jun 28 2021 Travis Holloway <t.holloway@cpanel.net> - 5.6.40-5
- EA-9013: Disable %check section

* Thu Apr 23 2020 Daniel Muey <dan@cpanel.net> - 5.6.40-4
- ZC-6611: Do not package empty share directories

* Thu Mar 05 2020 Daniel Muey <dan@cpanel.net> - 5.6.40-3
- ZC-6270: Fix circular deps like EA-8854

* Fri Mar 15 2019 Tim Mullin <tim@cpanel.net> - 5.6.40-2
- EA-8291: Fix pear installing before php-cli when installing ea-php56

* Tue Jan 15 2019 Cory McIntire <cory@cpanel.net> - 5.6.40-1
- Updated to version 5.6.40 via update_pkg.pl (EA-8158)

* Thu Dec 06 2018 Cory McIntire <cory@cpanel.net> - 5.6.39-1
- Updated to version 5.6.39 via update_pkg.pl (EA-8056)

* Fri Oct 26 2018 Tim Mullin <tim@cpanel.net> - 5.6.38-2
- EA-7957: Added ea-apache24-mod_proxy_fcgi as a dependency of php-fpm.

* Thu Sep 13 2018 Cory McIntire <cory@cpanel.net> - 5.6.38-1
- Updated to version 5.6.38 via update_pkg.pl (EA-7842)

* Tue Jul 24 2018 Cory McIntire <cory@cpanel.net> - 5.6.37-1
- Updated to version 5.6.37 via update_pkg.pl (EA-7732)

* Thu Apr 26 2018 Cory McIntire <cory@cpanel.net> - 5.6.36-1
- Updated to version 5.6.36 via update_pkg.pl (EA-7435)

* Mon Apr 02 2018 Daniel Muey <dan@cpanel.net> - 5.6.35-1
- EA-7355: Update to v5.6.35, drop v5.6.34

* Thu Mar 01 2018 Daniel Muey <dan@cpanel.net> - 5.6.34-1
- EA-7268: Update to v5.6.34, drop v5.6.33

* Thu Feb 15 2018 Daniel Muey <dan@cpanel.net> - 5.6.33-5
- EA-5277: Add conflicts for ea-php##-scldevel packages

* Wed Jan 17 2018 Daniel Muey <dan@cpanel.net> - 5.6.33-4
- EA-6958: Ensure ownership of _licensedir if it is set

* Tue Jan 09 2018 Dan Muey <dan@cpanel.net> - 5.6.33-3
- ZC-3247: Add support for the allowed-php list to WHM’s Feature Lists

* Tue Jan 09 2018 Rishwanth Yeddula <rish@cpanel.net> - 5.6.33-2
- ZC-3242: Ensure the runtime package requires the meta package

* Fri Jan 05 2018 Cory McIntire <cory@cpanel.net> - 5.6.33-1
- Updated to version 5.6.33 via update_pkg.pl (EA-7082)

* Fri Nov 03 2017 Dan Muey <dan@cpanel.net> - 5.6.32-2
- EA-3999: adjust files to get better cleanup on uninstall

* Fri Oct 27 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.32-1
- EA-6931: Updated to version 5.6.32

* Thu Jul 06 2017 Cory McIntire <cory@cpanel.net> - 5.6.31-1
- Updated to version 5.6.31 via update_pkg.pl (EA-6514)

* Fri Jan 20 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.30-1
- Updated PHP version

* Fri Dec 9 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.29-1
- Updated PHP version

* Thu Nov 10 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.28-1
- Updated PHP version

* Mon Oct 17 2016 Edwin Buck <e.buck@cpanel.net> - 5.6.27-1
- Updated PHP version

* Fri Sep 16 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.26-1
- Updated PHP version

* Fri Aug 19 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.25-1
- Updated PHP version

* Thu Jul 21 2016 Edwin Buck <e.buck@cpanel.net> - 5.6.24-1
- Updated PHP version

* Mon Jun 27 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.23-1
- Updated PHP version

* Mon Jun 20 2016 Dan Muey <dan@cpanel.net> - 5.6.22-3
- EA-4383: Update Release value to OBS-proof versioning

* Fri May 27 2016 Jacob Perkins <jacob.perkins@cpanelnet> 5.6.22-1
- Updated PHP version

* Thu Apr 28 2016 Jacob Perkins <jacob.perkins@cpanel.net> 5.6.21-1
- Updated PHP version

* Fri Apr 01 2016 Jacob Perkins <jacob.perkins@cpanel.net> 5.6.20-1
- Updated PHP version

* Fri Mar 04 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.19-1
- Updated PHP Version

* Thu Feb 04 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 5.6.18-1
- Updated PHP Version

* Wed Jun  3 2015 S. Kurt Newman <kurt.newman@cpanel.net> - 1.1-8
- Fix macros for namespaces that contain hyphens (-); ZC-560

* Fri Mar 06 2015 S. Kurt Newman <kurt.newman@cpanel.net> - 1.1-7
- Updated for PHP 5.6

* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-6
- Fix path typo in README
  Related: #1061455

* Wed Feb 12 2014 Remi Collet <rcollet@redhat.com> 1.1-5
- avoid empty debuginfo subpackage
- add LICENSE, README and php55.7 man page #1061455
- add scldevel subpackage #1063357

* Mon Jan 20 2014 Remi Collet <rcollet@redhat.com> 1.1-4
- rebuild with latest scl-utils #1054731

* Tue Nov 19 2013 Remi Collet <rcollet@redhat.com> 1.1-2
- fix scl_package_override

* Tue Nov 19 2013 Remi Collet <rcollet@redhat.com> 1.1-1
- build for RHSCL 1.1

* Tue Sep 17 2013 Remi Collet <rcollet@redhat.com> 1-1.5
- add macros.php55-build for scl_package_override

* Fri Aug  2 2013 Remi Collet <rcollet@redhat.com> 1-1
- initial packaging
