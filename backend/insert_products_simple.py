"""Script simplificat pentru inserarea produselor în Supabase - fără dependențe complexe."""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import direct fără websockets
try:
    from supabase import create_client
except ImportError as e:
    print("❌ Eroare: Supabase nu este instalat corect!")
    print(f"   Detalii: {e}")
    print("\n💡 Soluție:")
    print("   1. Activează virtual environment-ul:")
    print("      .\\venv\\Scripts\\activate  (Windows)")
    print("   2. Instalează dependențele:")
    print("      pip install -r requirements.txt")
    sys.exit(1)

from app.data import HARDCODED_PRODUCTS

def insert_all_products():
    """Inserează toate produsele din HARDCODED_PRODUCTS în Supabase."""
    # Conectare la Supabase
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Nu s-a putut conecta la Supabase!")
        print("Verifică că ai setat SUPABASE_URL și SUPABASE_KEY în .env")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"❌ Eroare la conectare Supabase: {e}")
        return False
    
    print("=" * 60)
    print("Inserare produse în Supabase")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    updated_count = 0
    
    for product in HARDCODED_PRODUCTS:
        product_id = product["id"]
        product_name = product["name"]
        
        try:
            # Verifică dacă produsul există deja
            response = supabase.table("produse").select("id").eq("id", product_id).execute()
            
            if response.data:
                # Produsul există - actualizează-l
                try:
                    # Pregătește datele pentru update
                    update_data = {k: v for k, v in product.items() if k != "id"}
                    supabase.table("produse").update(update_data).eq("id", product_id).execute()
                    print(f"🔄 '{product_name}' actualizat cu succes")
                    updated_count += 1
                except Exception as update_error:
                    print(f"⚠️  '{product_name}' există dar nu s-a putut actualiza: {update_error}")
                    skipped_count += 1
                continue
            
            # Inserează produsul nou
            supabase.table("produse").insert(product).execute()
            print(f"✅ '{product_name}' inserat cu succes")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Eroare la '{product_name}': {e}")
            error_count += 1
    
    print("\n" + "=" * 60)
    print("Rezumat:")
    print(f"  ✅ Inserate cu succes: {success_count}")
    print(f"  🔄 Actualizate: {updated_count}")
    print(f"  ⏭️  Sărite: {skipped_count}")
    print(f"  ❌ Erori: {error_count}")
    print(f"  📦 Total produse: {len(HARDCODED_PRODUCTS)}")
    print("=" * 60)
    
    # Verifică câte produse sunt acum în Supabase
    try:
        all_products = supabase.table("produse").select("id").execute()
        print(f"\n📊 Total produse în Supabase: {len(all_products.data)}")
    except Exception as e:
        print(f"\n⚠️  Nu s-a putut verifica numărul de produse: {e}")
    
    return error_count == 0

if __name__ == "__main__":
    success = insert_all_products()
    sys.exit(0 if success else 1)

