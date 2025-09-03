#!/usr/bin/env python3
"""
Helper script to get n8n API key
"""
import webbrowser
import time

def main():
    print("🔑 n8n API Key Setup Helper")
    print("=" * 40)
    print()
    print("To get your n8n API key, follow these steps:")
    print()
    print("1. 📱 Open your n8n instance in a browser")
    print("2. 🔧 Go to Settings (gear icon)")
    print("3. 🔑 Click on 'API Keys'")
    print("4. ➕ Click 'Create API Key'")
    print("5. 📝 Give it a name (e.g., 'AI Platform')")
    print("6. 📋 Copy the generated API key")
    print()
    print("💡 The API key will look like: 'n8n_api_xxxxxxxxxxxxxxxx'")
    print()
    
    # Ask if user wants to open n8n
    open_n8n = input("🌐 Open n8n in your browser now? (y/n): ").lower().strip()
    
    if open_n8n in ['y', 'yes']:
        print("🚀 Opening n8n...")
        webbrowser.open("http://localhost:5678")
        print("✅ n8n should now be open in your browser")
        print()
        print("📋 After getting your API key, you can:")
        print("   - Set it as environment variable: set N8N_API_KEY=your_key_here")
        print("   - Or use it directly: python -m ai_data_platform n8n setup --api-key your_key_here")
    else:
        print("📋 Manual steps:")
        print("   1. Go to: http://localhost:5678")
        print("   2. Follow the steps above to get your API key")
        print("   3. Use the key with the CLI commands")
    
    print()
    print("🎯 Next steps:")
    print("   1. Get your API key from n8n")
    print("   2. Run: python -m ai_data_platform n8n setup --api-key YOUR_KEY")
    print("   3. Test: python -m ai_data_platform n8n test --api-key YOUR_KEY")
    print("   4. Run ingestion: python -m ai_data_platform n8n ingest --api-key YOUR_KEY")

if __name__ == "__main__":
    main()

