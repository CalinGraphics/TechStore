import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { ShoppingCart, User, LogOut, Zap, Laptop, Smartphone, Star, Trash2, Plus, Minus, Filter, Tag, Store, DollarSign } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

// Login Page
const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password,
      });
      
      onLogin(response.data);
      toast.success(`Bun venit, ${response.data.username}!`);
    } catch (error) {
      toast.error("Autentificare eșuată. Verifică username-ul și parola.");
      console.error("Login error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>
      
      <div className="login-card-wrapper">
        <Card className="login-card" data-testid="login-card">
          <CardHeader className="text-center">
            <div className="logo-container">
              <Zap className="logo-icon" />
            </div>
            <CardTitle className="login-title">TechStore</CardTitle>
            <CardDescription className="login-subtitle">
              Recomandări personalizate pentru tine
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="login-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <Input
                  id="username"
                  data-testid="username-input"
                  type="text"
                  placeholder="john_tech"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label htmlFor="password">Parolă</label>
                <Input
                  id="password"
                  data-testid="password-input"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="form-input"
                />
              </div>
              <Button
                data-testid="login-button"
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading ? "Se încarcă..." : "Autentificare"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Product Card Component
const ProductCard = ({ product, onClick, isRecommended = false, onAddToCart }) => {
  const handleAddToCart = (e) => {
    e.stopPropagation();
    onAddToCart(product);
  };

  return (
    <Card 
      className="product-card" 
      onClick={onClick}
      data-testid={`product-card-${product.id}`}
    >
      {isRecommended && (
        <div className="recommended-badge">
          <Star className="w-3 h-3" />
          <span>Recomandat</span>
        </div>
      )}
      <div className="product-image-container">
        <img
          src={product.image_url}
          alt={product.name}
          className="product-image"
          onError={(e) => {
            e.target.src = "https://via.placeholder.com/300x200?text=No+Image";
          }}
        />
      </div>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="product-name">{product.name}</CardTitle>
          <Badge className="brand-badge">{product.brand}</Badge>
        </div>
        <CardDescription className="product-description">
          {product.description}
        </CardDescription>
      </CardHeader>
      <CardFooter className="product-footer">
        <div className="price-tag">{product.price.toFixed(2)} RON</div>
        <div className="flex gap-2">
          <Button 
            className="add-to-cart-mini-btn" 
            onClick={handleAddToCart}
            data-testid={`add-to-cart-${product.id}`}
          >
            <ShoppingCart className="w-4 h-4" />
          </Button>
          <Button className="view-details-btn" data-testid={`view-product-${product.id}`}>
            Detalii
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

// Dashboard Page
const Dashboard = ({ user, onLogout, cart, setCart }) => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recommendationReason, setRecommendationReason] = useState("");
  const [cartOpen, setCartOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState("");
  const [filterBrand, setFilterBrand] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch recommendations
      const recResponse = await axios.get(`${API}/recommendations/${user.user_id}`);
      setRecommendations(recResponse.data.products);
      setRecommendationReason(recResponse.data.reason);
      
      // Initial fetch of products (no filters) so the page is not empty
      const productsResponse = await axios.get(`${API}/products`);
      setAllProducts(productsResponse.data);
    } catch (error) {
      toast.error("Eroare la încărcarea produselor");
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = useCallback(async () => {
    try {
      const params = {
        category: filterCategory || undefined,
        brand: filterBrand || undefined,
        price_min: priceMin !== "" ? Number(priceMin) : undefined,
        price_max: priceMax !== "" ? Number(priceMax) : undefined,
      };
      const response = await axios.get(`${API}/products`, { params });
      setAllProducts(response.data);
    } catch (error) {
      toast.error("Eroare la filtrarea produselor");
      console.error("Filter fetch error:", error);
    }
  }, [filterCategory, filterBrand, priceMin, priceMax]);

  useEffect(() => {
    // Refetch products when filters change
    fetchProducts();
  }, [fetchProducts]);

  const handleProductClick = (productId) => {
    navigate(`/product/${productId}`);
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
      toast.success(`${product.name} - cantitate actualizată`);
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
      toast.success(`${product.name} adăugat în coș`);
    }
  };

  const updateQuantity = (productId, delta) => {
    setCart(cart.map(item => {
      if (item.id === productId) {
        const newQuantity = item.quantity + delta;
        if (newQuantity <= 0) return null;
        return { ...item, quantity: newQuantity };
      }
      return item;
    }).filter(Boolean));
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
    toast.info("Produs eliminat din coș");
  };

  const getTotalPrice = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const getTotalItems = () => {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
  };

  const handleCheckout = () => {
    if (cart.length === 0) {
      toast.error("Coșul este gol");
      return;
    }
    
    toast.success("Comandă procesată cu succes!");
    setCart([]);
    setCartOpen(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Se încarcă...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container" data-testid="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section">
            <Zap className="header-logo" />
            <h1 className="header-title">TechStore</h1>
          </div>
          <div className="user-section">
            <div className="user-info">
              <User className="user-icon" />
              <span className="user-name" data-testid="user-name">{user.username}</span>
            </div>
            
            {/* Shopping Cart Sheet */}
            <Sheet open={cartOpen} onOpenChange={setCartOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="cart-btn"
                  data-testid="cart-button"
                >
                  <ShoppingCart className="w-4 h-4" />
                  {getTotalItems() > 0 && (
                    <Badge className="cart-badge" data-testid="cart-count">{getTotalItems()}</Badge>
                  )}
                </Button>
              </SheetTrigger>
              <SheetContent className="cart-sheet" data-testid="cart-sheet">
                <SheetHeader>
                  <SheetTitle className="cart-title">Coșul tău</SheetTitle>
                  <SheetDescription>
                    {cart.length} produse în coș
                  </SheetDescription>
                </SheetHeader>
                
                <div className="cart-items" data-testid="cart-items">
                  {cart.length === 0 ? (
                    <div className="empty-cart">
                      <ShoppingCart className="empty-cart-icon" />
                      <p>Coșul este gol</p>
                    </div>
                  ) : (
                    cart.map(item => (
                      <div key={item.id} className="cart-item" data-testid={`cart-item-${item.id}`}>
                        <img src={item.image_url} alt={item.name} className="cart-item-image" />
                        <div className="cart-item-info">
                          <h4 className="cart-item-name">{item.name}</h4>
                          <p className="cart-item-price">{item.price.toFixed(2)} RON</p>
                          <div className="cart-item-quantity">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => updateQuantity(item.id, -1)}
                              data-testid={`decrease-${item.id}`}
                            >
                              <Minus className="w-3 h-3" />
                            </Button>
                            <span data-testid={`quantity-${item.id}`}>{item.quantity}</span>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => updateQuantity(item.id, 1)}
                              data-testid={`increase-${item.id}`}
                            >
                              <Plus className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFromCart(item.id)}
                          className="cart-item-remove"
                          data-testid={`remove-${item.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))
                  )}
                </div>

                {cart.length > 0 && (
                  <SheetFooter className="cart-footer">
                    <div className="cart-total">
                      <span>Total:</span>
                      <span className="cart-total-price" data-testid="cart-total">
                        {getTotalPrice().toFixed(2)} RON
                      </span>
                    </div>
                    <Button 
                      className="checkout-btn" 
                      onClick={handleCheckout}
                      data-testid="checkout-button"
                    >
                      Finalizează comanda
                    </Button>
                  </SheetFooter>
                )}
              </SheetContent>
            </Sheet>

            <Button
              variant="outline"
              size="sm"
              onClick={onLogout}
              className="logout-btn"
              data-testid="logout-button"
            >
              <LogOut className="w-4 h-4" />
              Ieșire
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        <Tabs defaultValue="recommendations" className="dashboard-tabs">
          <TabsList className="tabs-list">
            <TabsTrigger value="recommendations" data-testid="recommendations-tab">Pentru Tine</TabsTrigger>
            <TabsTrigger value="all" data-testid="all-products-tab">Toate Produsele</TabsTrigger>
          </TabsList>

          <TabsContent value="recommendations" className="tab-content">
            <div className="recommendations-section">
              <div className="section-header">
                <h2 className="section-title">Recomandări Personalizate</h2>
                <p className="section-description" data-testid="recommendation-reason">{recommendationReason}</p>
              </div>
              <div className="products-grid" data-testid="recommendations-grid">
                {recommendations.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onClick={() => handleProductClick(product.id)}
                    onAddToCart={addToCart}
                    isRecommended={true}
                  />
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="all" className="tab-content">
            <div className="all-products-section">
              <div className="section-header">
                <h2 className="section-title">Toate Produsele</h2>
                <p className="section-description">Explorează întreaga noastră colecție</p>
              </div>
              <div className="filters-panel" data-testid="filters-bar">
                <div className="filters-header">
                  <div className="filters-title">
                    <Filter className="filters-icon" />
                    <div>
                      <h3>Filtrează produsele</h3>
                      <p>Alege criteriile care te interesează și rafinează lista.</p>
                    </div>
                  </div>
                  <div className="filters-actions">
                    <Button
                      variant="ghost"
                      onClick={() => {
                        setFilterCategory("");
                        setFilterBrand("");
                        setPriceMin("");
                        setPriceMax("");
                      }}
                      data-testid="reset-filters"
                    >
                      Resetează
                    </Button>
                    <Button variant="outline" onClick={fetchProducts} data-testid="apply-filters">
                      Aplică
                    </Button>
                  </div>
                </div>
                <div className="filters-grid">
                  <div className="filter-field">
                    <label htmlFor="category">Categorie</label>
                    <div className="filter-input-wrapper">
                      <Tag className="filter-field-icon" />
                      <Select
                        value={filterCategory || "all"}
                        onValueChange={(value) =>
                          setFilterCategory(value === "all" ? "" : value)
                        }
                      >
                        <SelectTrigger className="filter-select-trigger" data-testid="filter-category">
                          <SelectValue placeholder="Toate categoriile" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Toate</SelectItem>
                          <SelectItem value="smartphones">Smartphones</SelectItem>
                          <SelectItem value="laptops">Laptops</SelectItem>
                          <SelectItem value="gaming">Gaming</SelectItem>
                          <SelectItem value="audio">Audio</SelectItem>
                          <SelectItem value="fitness">Fitness</SelectItem>
                          <SelectItem value="tablets">Tablets</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="filter-field">
                    <label htmlFor="brand">Brand</label>
                    <div className="filter-input-wrapper">
                      <Store className="filter-field-icon" />
                      <Input
                        id="brand"
                        placeholder="ex: Apple, Samsung"
                        value={filterBrand}
                        onChange={(e) => setFilterBrand(e.target.value)}
                        data-testid="filter-brand"
                        className="filter-input"
                      />
                    </div>
                  </div>
                  <div className="filter-field">
                    <label htmlFor="min-price">Preț minim</label>
                    <div className="filter-input-wrapper">
                      <DollarSign className="filter-field-icon" />
                      <Input
                        id="min-price"
                        type="number"
                        placeholder="Min"
                        value={priceMin}
                        onChange={(e) => setPriceMin(e.target.value)}
                        data-testid="filter-price-min"
                        className="filter-input"
                      />
                    </div>
                  </div>
                  <div className="filter-field">
                    <label htmlFor="max-price">Preț maxim</label>
                    <div className="filter-input-wrapper">
                      <DollarSign className="filter-field-icon" />
                      <Input
                        id="max-price"
                        type="number"
                        placeholder="Max"
                        value={priceMax}
                        onChange={(e) => setPriceMax(e.target.value)}
                        data-testid="filter-price-max"
                        className="filter-input"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="products-grid" data-testid="all-products-grid">
                {allProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onClick={() => handleProductClick(product.id)}
                    onAddToCart={addToCart}
                  />
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

// Product Details Page
const ProductDetails = ({ user, onLogout, cart, setCart }) => {
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const productId = window.location.pathname.split("/").pop();

  useEffect(() => {
    fetchProduct();
  }, [productId]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`${API}/products/${productId}`);
      setProduct(response.data);
    } catch (error) {
      toast.error("Eroare la încărcarea produsului");
      console.error("Fetch error:", error);
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const addToCart = () => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
      toast.success(`${product.name} - cantitate actualizată`);
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
      toast.success(`${product.name} adăugat în coș`);
    }
  };

  const getTotalItems = () => {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Se încarcă...</p>
      </div>
    );
  }

  if (!product) return null;

  return (
    <div className="product-details-container" data-testid="product-details">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section" onClick={() => navigate("/dashboard")} style={{ cursor: "pointer" }}>
            <Zap className="header-logo" />
            <h1 className="header-title">TechStore</h1>
          </div>
          <div className="user-section">
            <div className="user-info">
              <User className="user-icon" />
              <span className="user-name">{user.username}</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/dashboard")}
              className="cart-btn"
            >
              <ShoppingCart className="w-4 h-4" />
              {getTotalItems() > 0 && (
                <Badge className="cart-badge">{getTotalItems()}</Badge>
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onLogout}
              className="logout-btn"
            >
              <LogOut className="w-4 h-4" />
              Ieșire
            </Button>
          </div>
        </div>
      </header>

      {/* Product Details */}
      <main className="product-details-main">
        <Button
          variant="outline"
          onClick={() => navigate("/dashboard")}
          className="back-button"
          data-testid="back-button"
        >
          ← Înapoi
        </Button>

        <div className="product-details-content">
          <div className="product-image-section">
            <img
              src={product.image_url}
              alt={product.name}
              className="detail-product-image"
              data-testid="product-image"
              onError={(e) => {
                e.target.src = "https://via.placeholder.com/600x400?text=No+Image";
              }}
            />
          </div>

          <div className="product-info-section">
            <Badge className="category-badge" data-testid="product-category">{product.category}</Badge>
            <h1 className="product-detail-title" data-testid="product-name">{product.name}</h1>
            <div className="brand-info">
              <span className="brand-label">Brand:</span>
              <span className="brand-value" data-testid="product-brand">{product.brand}</span>
            </div>
            <p className="product-detail-description" data-testid="product-description">{product.description}</p>

            <div className="specs-section">
              <h3 className="specs-title">Specificații</h3>
              <div className="specs-grid" data-testid="product-specs">
                {Object.entries(product.specs).map(([key, value]) => (
                  <div key={key} className="spec-item">
                    <span className="spec-key">{key.replace("_", " ")}:</span>
                    <span className="spec-value">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="price-section">
              <div className="price-large" data-testid="product-price">{product.price.toFixed(2)} RON</div>
              <Button 
                className="add-to-cart-btn" 
                onClick={addToCart}
                data-testid="add-to-cart-button"
              >
                <ShoppingCart className="w-5 h-5" />
                Adaugă în coș
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState([]);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    setCart([]);
    localStorage.removeItem("user");
    localStorage.removeItem("cart");
    toast.info("Te-ai deconectat cu succes");
  };

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    
    const savedCart = localStorage.getItem("cart");
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  }, []);

  useEffect(() => {
    if (cart.length > 0) {
      localStorage.setItem("cart", JSON.stringify(cart));
    } else {
      localStorage.removeItem("cart");
    }
  }, [cart]);

  return (
    <div className="App">
      <Toaster position="top-right" richColors />
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={handleLogin} />
            }
          />
          <Route
            path="/dashboard"
            element={
              user ? (
                <Dashboard user={user} onLogout={handleLogout} cart={cart} setCart={setCart} />
              ) : (
                <Navigate to="/" />
              )
            }
          />
          <Route
            path="/product/:id"
            element={
              user ? (
                <ProductDetails user={user} onLogout={handleLogout} cart={cart} setCart={setCart} />
              ) : (
                <Navigate to="/" />
              )
            }
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;