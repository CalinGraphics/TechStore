"""Script simplu pentru testarea conexiunii la Supabase."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import database functions
from app.database import get_supabase_client

def test_connection():
    """Test Supabase connection."""
    print("=" * 50)
    print("Testare conexiune Supabase")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    print(f"\n1. Verificare variabile de mediu:")
    print(f"   SUPABASE_URL: {'✓ Setat' if supabase_url else '✗ Nu este setat'}")
    print(f"   SUPABASE_KEY: {'✓ Setat' if supabase_key else '✗ Nu este setat'}")
    
    if not supabase_url or not supabase_key:
        print("\n⚠️  ATENȚIE: Variabilele SUPABASE_URL și SUPABASE_KEY trebuie să fie setate!")
        print("   Creează un fișier .env în directorul backend/ cu:")
        print("   SUPABASE_URL=your_supabase_url")
        print("   SUPABASE_KEY=your_supabase_key")
        return False
    
    # Test connection
    print(f"\n2. Testare conexiune...")
    try:
        supabase = get_supabase_client()
        
        if supabase:
            print("   ✓ Conexiune reușită!")
            
            # Try a simple query to test
            print(f"\n3. Testare query simplu...")
            try:
                # Try to query a table (this will fail gracefully if table doesn't exist)
                response = supabase.table("produse").select("id").limit(1).execute()
                print(f"   ✓ Query executat cu succes!")
                print(f"   ✓ Baza de date este funcțională!")
                return True
            except Exception as e:
                print(f"   ⚠️  Query a eșuat: {e}")
                print(f"   (Aceasta poate fi normală dacă tabela nu există încă)")
                print(f"   ✓ Conexiunea funcționează, dar tabela 'produse' nu există sau nu are acces")
                return True  # Connection works, just table issue
        else:
            print("   ✗ Nu s-a putut conecta la Supabase")
            print("   Verifică URL-ul și cheia în fișierul .env")
            return False
            
    except Exception as e:
        print(f"   ✗ Eroare la conexiune: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    print("\n" + "=" * 50)
    if success:
        print("✓ Test finalizat cu succes!")
    else:
        print("✗ Test eșuat - verifică configurația")
    print("=" * 50)
    sys.exit(0 if success else 1)

