#!/bin/bash

# OpenSeal Universal Linux Installer
# Bastion Open Foundation Initiative

echo "------------------------------------------"
echo "🛠️  Installing OpenSeal PGP Vault..."
echo "------------------------------------------"

# 1. Install Dependencies (Python3, Tkinter, GnuPG)
echo "📦 Checking system dependencies..."
if [ -f /etc/debian_version ]; then
    sudo apt update && sudo apt install -y python3-tk python3-gnupg gnupg
elif [ -f /etc/arch-release ]; then
    sudo pacman -Sy --noconfirm tk python-gnupg gnupg
elif [ -f /etc/fedora-release ]; then
    sudo dnf install -y python3-tkinter python3-gnupg gnupg
else
    echo "⚠️  Unknown OS. Please ensure python3-tk and gnupg are installed manually."
fi

# 2. Setup Directories
INSTALL_DIR="/opt/openseal"
ICON_DIR="$INSTALL_DIR/images"

echo "📂 Creating installation directory at $INSTALL_DIR..."
sudo mkdir -p $ICON_DIR

# 3. Copy Application Files
# Assuming your main script is named openseal.py
sudo cp openseal.py $INSTALL_DIR/
if [ -d "images" ]; then
    sudo cp images/logo.png $ICON_DIR/
else
    echo "⚠️  Warning: images/logo.png not found. Desktop icon may be blank."
fi

# 4. Create the Launcher Script
echo "📜 Creating execution wrapper..."
echo -e "#!/bin/bash\npython3 $INSTALL_DIR/openseal.py" | sudo tee /usr/local/bin/openseal > /dev/null
sudo chmod +x /usr/local/bin/openseal

# 5. Create Desktop Entry
echo "🖥️  Creating Desktop Entry..."
cat <<EOF > openseal.desktop
[Desktop Entry]
Name=OpenSeal
Comment=Secure PGP Vault & File Sealer
Exec=openseal
Icon=$ICON_DIR/logo.png
Terminal=false
Type=Application
Categories=Utility;Security;
Keywords=PGP;Encryption;Vault;
EOF

sudo mv openseal.desktop /usr/share/applications/

echo "------------------------------------------"
echo "✅ Installation Complete!"
echo "🚀 You can now launch 'OpenSeal' from your app menu."
echo "------------------------------------------"
