import os
import subprocess
import sys

def run_command(command, description, interactive=False):
    print(f"\n[INFO] {description}")
    print(f"Running: {command}")
    if interactive:
        os.system(command)
    else:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Command failed: {result.stderr}")
            sys.exit(1)
        print(f"[INFO] Output: {result.stdout}")

def create_project_structure():
    print("[INFO] Creating project structure...")
    os.makedirs("geoip-visualizer/src", exist_ok=True)
    os.makedirs("geoip-visualizer/files", exist_ok=True)

    with open("geoip-visualizer/src/geoip_visualizer.py", "w") as app_file:
        app_file.write("""\
import folium

def create_map():
    m = folium.Map(location=[20, 0], zoom_start=2)
    m.save('/tmp/geoip_status_map.html')
if __name__ == '__main__':
    create_map()
""")

    with open("geoip-visualizer/files/GeoIP.conf", "w") as config_file:
        config_file.write("GeoIP2City:\n  URL: https://geoip.maxmind.com\n  LicenseKey: your_license_key\n")

    with open("geoip-visualizer/Makefile", "w") as makefile:
        makefile.write("""\
include $(TOPDIR)/rules.mk

PKG_NAME:=geoip-visualizer
PKG_VERSION:=1.0
PKG_RELEASE:=1

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)
PKG_MAINTAINER:=Your Name <youremail@example.com>
PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=LICENSE

include $(INCLUDE_DIR)/package.mk

define Package/geoip-visualizer
    SECTION:=net
    CATEGORY:=Network
    TITLE:=GeoIP Visualizer
    DEPENDS:=+python3 +python3-requests +python3-flask
endef

define Package/geoip-visualizer/description
    A tool for visualizing GeoIP configuration and status using MaxMind data.
endef

define Build/Prepare
    mkdir -p $(PKG_BUILD_DIR)
    $(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Build/Compile
    # No compilation required; this is a Python application.
endef

define Package/geoip-visualizer/install
    $(INSTALL_DIR) $(1)/usr/bin
    $(INSTALL_BIN) $(PKG_BUILD_DIR)/geoip_visualizer.py $(1)/usr/bin/
    $(INSTALL_DIR) $(1)/etc/config
    $(INSTALL_DATA) ./files/GeoIP.conf $(1)/etc/config/
endef

$(eval $(call BuildPackage,geoip-visualizer))
""")

    print("[INFO] Project structure created successfully.")

def build_package():
    print("[INFO] Building package...")
    sdk_path = input("Enter the path to your OpenWrt SDK: ").strip()
    os.chdir(sdk_path)

    package_path = os.path.abspath("geoip-visualizer")
    run_command(f"ln -s {package_path} package/geoip-visualizer", "Linking package into SDK")

    run_command("make menuconfig", "Opening menuconfig to select the package", interactive=True)
    run_command("make package/geoip-visualizer/compile V=s", "Building the package")

def install_package():
    print("[INFO] Installing package on OpenWrt...")
    ipk_path = input("Enter the path to the built .ipk file: ").strip()
    openwrt_ip = input("Enter the IP address of your OpenWrt device: ").strip()

    run_command(f"scp {ipk_path} root@{openwrt_ip}:/tmp/", "Copying .ipk to OpenWrt")
    run_command(f"ssh root@{openwrt_ip} opkg install /tmp/{os.path.basename(ipk_path)}", "Installing package on OpenWrt")

def main():
    print("[INFO] Starting the GeoIP Visualizer application creation process.")
    create_project_structure()

    print("\n[INFO] Next steps:")
    print("1. Navigate to the OpenWrt SDK directory.")
    print("2. Link the 'geoip-visualizer' directory to the 'package/' directory in the SDK.")
    print("3. Run 'make menuconfig' to select the 'geoip-visualizer' package.")
    print("4. Build the package using 'make package/geoip-visualizer/compile V=s'.")
    print("5. Use SCP to transfer the .ipk file to your OpenWrt device.")
    print("6. Install the package using 'opkg install /tmp/<your_package>.ipk'.")
    print("\nDo you want me to run these steps for you automatically? (yes/no)")

    if input().strip().lower() == "yes":
        build_package()
        install_package()
    else:
        print("[INFO] Manual steps enabled. Follow the instructions above.")

if __name__ == "__main__":
    main()
