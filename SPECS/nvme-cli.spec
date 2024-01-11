#%%global commit0 bdbb4da0979fbdc079cf98410cdb31cf799e83b3
#%%global shortcommit0 %%(c=%%{commit0}; echo ${c:0:7})

Name:           nvme-cli
Version:        2.4
Release:        10%{?dist}
Summary:        NVMe management command line interface

License:        GPLv2+
URL:            https://github.com/linux-nvme/nvme-cli
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

Patch0:         0001-nbft-make-lookup_ctrl-function-public.patch
Patch1:         0002-nbft-added-NBFT-v1.0-table-support.patch
Patch2:         0003-nbft-add-the-nbft-show-plugin.patch
Patch3:         0004-Revert-nvme-Masks-SSTAT-in-sanize-log-output.patch
Patch4:         0005-util-Fix-suffix_si_parse-to-parse-no-decimal-point-b.patch

BuildRequires:  meson >= 0.50.0
BuildRequires:  gcc gcc-c++
BuildRequires:  libuuid-devel
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  zlib-devel
BuildRequires:  libnvme-devel >= 1.4-5
BuildRequires:  json-c-devel >= 0.14
BuildRequires:  asciidoc
BuildRequires:  xmlto

Requires:       util-linux

%description
nvme-cli provides NVM-Express user space tooling for Linux.

%prep
#%%setup -qn %%{name}-%%{commit0}
%setup -q

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%meson -Dudevrulesdir=%{_udevrulesdir} -Dsystemddir=%{_unitdir} -Ddocs=all -Ddocs-build=true -Dhtmldir=%{_pkgdocdir}
%meson_build

%install
%meson_install

# Do not install the dracut rule yet.  See rhbz 1742764
# Do we want to keep this here?  Now that we have boot support for nvme/fc + tcp?
rm -f %{buildroot}/usr/lib/dracut/dracut.conf.d/70-nvmf-autoconnect.conf

# Move html docs into the right place
mv %{buildroot}%{_pkgdocdir}/nvme %{buildroot}%{_pkgdocdir}/html
rm -rf %{buildroot}%{_pkgdocdir}/nvme

%files
%license LICENSE
%doc README.md
%doc %{_pkgdocdir}/*
%{_sbindir}/nvme
%{_mandir}/man1/nvme*.gz
%{_datadir}/bash-completion/completions/nvme
%{_datadir}/zsh/site-functions/_nvme
%dir %{_sysconfdir}/nvme
%config(noreplace) %{_sysconfdir}/nvme/discovery.conf
%{_unitdir}/nvmefc-boot-connections.service
%{_unitdir}/nvmf-autoconnect.service
%{_unitdir}/nvmf-connect.target
%{_unitdir}/nvmf-connect@.service
%{_udevrulesdir}/70-nvmf-autoconnect.rules
%{_udevrulesdir}/71-nvmf-iopolicy-netapp.rules
# Do not install the dracut rule yet.  See rhbz 1742764
# Is this still true?  Now that we support nvme-of boot, do we want to install this file?
# /usr/lib/dracut/dracut.conf.d/70-nvmf-autoconnect.conf

%post
if [ $1 -eq 1 ] || [ $1 -eq 2 ]; then
        if [ ! -s %{_sysconfdir}/nvme/hostnqn ]; then
            echo $(nvme gen-hostnqn) > %{_sysconfdir}/nvme/hostnqn
        fi
        if [ ! -s %{_sysconfdir}/nvme/hostid ]; then
            echo $(nvme show-hostnqn | sed 's/^.*uuid://') > %{_sysconfdir}/nvme/hostid
        fi

    # apply udev and systemd changes that we did
    if [ $1 -eq 1 ]; then
        systemctl enable nvmefc-boot-connections
    fi
    systemctl daemon-reload
    udevadm control --reload-rules && udevadm trigger
    exit 0
fi

%changelog
* Mon Aug 21 2023 John Meneghini <jmeneghi@redhat.com> - 2.4-10
- JIRA: https://issues.redhat.com/browse/RHEL-1492

* Thu Aug 10 2023 John Meneghini <jmeneghi@redhat.com> - 2.4-9
- JIRA: https://issues.redhat.com/browse/RHEL-1147

* Mon Jul 17 2023 John Meneghini <jmeneghi@redhat.com> - 2.4-8
- Fix BZ#2223436

* Wed Jun 14 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-7
- Fix BZ#2210656

* Tue May 30 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-6
- Rebuild for #2208399

* Thu May 25 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-5
- Fix SSTAT print (BZ2208399)

* Tue May 16 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-4
- Add support to NBFT (BZ2188518)

* Fri May 12 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-3
- Fix a warning when building the package BZ2195897

* Wed May 03 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-2
- Fix a bogus changelog date BZ2186074

* Mon Apr 03 2023 Maurizio Lombardi <mlombard@redhat.com> - 2.4-1
- Update to version v2.4

* Thu Nov 10 2022 Maurizio Lombardi <mlombard@redhat.com> - 2.1.2-2
- Do not re-enable nvmefc-boot-connections when the package gets updated

* Mon Sep 26 2022 Maurizio Lombardi <mlombard@redhat.com> - 2.1.2-1
- Update to version v2.1.2

* Mon Aug 29 2022 Maurizio Lombardi <mlombard@redhat.com> - 2.0-4
- Fix BZ2104945

* Fri Jul 15 2022 Maurizio Lombardi <mlombard@redhat.com> - 2.0-3
- Fix BZ2105742

* Thu Jun 16 2022 Maurizio Lombardi <mlombard@redhat.com> - 2.0-2
- Fix the gating tests

* Wed Apr 27 2022 Maurizio Lombardi <mlombard@redhat.com> - 2.0-1
- Upgrade to version 2.0

* Mon Feb 07 2022 Maurizio Lombardi <mlombard@redhat.com> - 1.16-3
- Add a few bugfixes

* Mon Dec 13 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.16-2
- Update to the latest version

* Thu Dec 09 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.14-4
- Fix handling of the ctrl_loss_tmo parameter

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Mon Jun 14 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.14-2
- Fix for bz1962422 (nvme flush failed from from v5.13-rc1)

* Mon May 03 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.14-1
- Update to the latest upstream version

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Mar 19 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.12-1
- Update to 1.13 and add postin scriptlet

* Sat Apr 25 2020 luto@kernel.org - 1.11.1-1
- Update to 1.11

* Thu Mar 19 2020 luto@kernel.org - 1.10.1-1
- Update to 1.10.1

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Oct 02 2019 luto@kernel.org - 1.9-1
- Update to 1.9
- Certain fabric functionality may not work yet due to missing dracut
  support and missing hostid and hostnqn configuration.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Apr 15 2019 luto@kernel.org - 1.8.1-1
- Update to 1.8.1-1.
- Remove a build hack.

* Sun Feb 24 2019 luto@kernel.org - 1.7-2
- Create /etc/nvme

* Sun Feb 24 2019 luto@kernel.org - 1.7-1
- Bump to 1.7
- Clean up some trivial rpmlint complaints

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jul 24 2018 luto@kernel.org - 1.6-1
- Update to 1.6

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Nov 22 2017 luto@kernel.org - 1.4-1
- Update to 1.4

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 22 2017 luto@kernel.org - 1.3-1
- Update to 1.3

* Wed Apr 19 2017 luto@kernel.org - 1.2-2
- Update to 1.2
- 1.2-1 never existed

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 luto@kernel.org - 1.1-1
- Update to 1.1

* Sun Nov 20 2016 luto@kernel.org - 1.0-1
- Update to 1.0

* Mon Oct 31 2016 luto@kernel.org - 0.9-1
- Update to 0.9

* Thu Jun 30 2016 luto@kernel.org - 0.8-1
- Update to 0.8

* Tue May 31 2016 luto@kernel.org - 0.7-1
- Update to 0.7

* Fri Mar 18 2016 luto@kernel.org - 0.5-1
- Update to 0.5

* Sun Mar 06 2016 luto@kernel.org - 0.4-1
- Update to 0.4

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.2-3.20160112gitbdbb4da
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 luto@kernel.org - 0.2-2.20160112gitbdbb4da
- Update to new upstream commit, fixing #49.  "nvme list" now works.

* Wed Jan 13 2016 luto@kernel.org - 0.2-1.20160112gitde3e0f1
- Initial import.
