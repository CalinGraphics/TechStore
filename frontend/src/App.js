import { useState, useEffect } from "react";
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
import {
  ShoppingCart,
  User,
  LogOut,
  Zap,
  Laptop,
  Smartphone,
  Star,
  Trash2,
  Plus,
  Minus,
  Settings,
  Edit,
  Package,
  UserCircle,
  Camera,
  Save,
  ArrowLeft,
  Heart,
  History,
  Check,
} from "lucide-react";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;
const PROFILE_OVERRIDES_KEY = "userProfileOverrides";

const safeSetItem = (key, value) => {
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    console.warn("localStorage.setItem failed:", error);
  }
};

const safeRemoveItem = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.warn("localStorage.removeItem failed:", error);
  }
};

const getProfileOverrides = () => {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_OVERRIDES_KEY) || "{}");
  } catch {
    return {};
  }
};

const applyProfileOverrides = (userData) => {
  const overrides = getProfileOverrides();
  const override = overrides[userData?.user_id];
  if (!override) {
    return userData;
  }

  return {
    ...userData,
    profile: {
      ...userData.profile,
      ...(override.profile || {}),
    },
    profileImage: override.profileImage ?? userData.profileImage,
  };
};

const saveProfileOverrides = (userId, override) => {
  const overrides = getProfileOverrides();
  overrides[userId] = override;
  safeSetItem(PROFILE_OVERRIDES_KEY, JSON.stringify(overrides));
};

const parseListInput = (value = "") =>
  value
    .split(",")
    .map((item) => item.replace(/[\[\]"]/g, "").trim())
    .filter(Boolean);

const formatListInput = (list = []) => {
  if (!list) return "";
  if (Array.isArray(list)) {
    return list.join(", ");
  }
  return String(list);
};

const INTEREST_OPTIONS = [
  { value: "laptops", label: "Laptops" },
  { value: "smartphones", label: "Smartphones" },
  { value: "gaming", label: "Gaming" },
  { value: "audio", label: "Audio" },
  { value: "fitness", label: "Wearables & Fitness" },
  { value: "tablets", label: "Tablete" },
];

const INTEREST_LABELS = INTEREST_OPTIONS.reduce((acc, option) => {
  acc[option.value] = option.label;
  return acc;
}, {});

const BUDGET_LABELS = {
  low: "Buget redus (<500 RON)",
  medium: "Buget mediu (500 - 1200 RON)",
  high: "Buget ridicat (>1200 RON)",
};

const AVATAR_MAX_SIZE = 512;

const readFileAsDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result?.toString() || "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

const compressImageDataUrl = (dataUrl) =>
  new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      let { width, height } = image;
      if (width > AVATAR_MAX_SIZE || height > AVATAR_MAX_SIZE) {
        const ratio = Math.min(AVATAR_MAX_SIZE / width, AVATAR_MAX_SIZE / height);
        width = Math.round(width * ratio);
        height = Math.round(height * ratio);
      }
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        reject(new Error("Canvas context missing"));
        return;
      }
      ctx.drawImage(image, 0, 0, width, height);
      resolve(canvas.toDataURL("image/jpeg", 0.85));
    };
    image.onerror = reject;
    image.src = dataUrl;
  });

const ProfileSummary = ({ profile, profileImage }) => {
  if (!profile) return null;

  const normalizeList = (list) =>
    list
      .map((entry) => {
        if (typeof entry === "string") {
          return entry.trim();
        }

        if (entry && typeof entry === "object") {
          if ("label" in entry && typeof entry.label === "string") {
            return entry.label.trim();
          }
          if ("name" in entry && typeof entry.name === "string") {
            return entry.name.trim();
          }
          return String(entry).trim();
        }

        if (entry === null || entry === undefined) {
          return "";
        }

        return String(entry).trim();
      })
      .filter(Boolean);

  const toArray = (value) => {
    if (!value) return [];

    if (Array.isArray(value)) {
      return normalizeList(value);
    }

    if (typeof value === "string") {
      // Try JSON first (covers strings saved like '["smartphones","fitness"]')
      try {
        const parsed = JSON.parse(value);
        if (Array.isArray(parsed)) {
          return normalizeList(parsed);
        }
      } catch {
        // fall through to manual split
      }

      return normalizeList(
        value
          .split(",")
          .map((entry) => entry.replace(/[\[\]"]/g, "").trim())
      );
    }

    if (typeof value === "object") {
      return normalizeList(Object.values(value));
    }

    return normalizeList([value]);
  };

  const interests = toArray(profile.interests);
  const preferredBrands = toArray(profile.preferred_brands);
  const formatInterestLabel = (value) => INTEREST_LABELS[value] || value;

  return (
    <div className="profile-summary-card" data-testid="profile-summary">
      <div className="profile-summary-header">
        <div className="profile-avatar-wrapper">
          {profileImage ? (
            <img src={profileImage} alt="Profil" className="profile-summary-avatar" />
          ) : (
            <Laptop className="profile-summary-icon" />
          )}
        </div>
        <div>
          <p className="profile-summary-label">Profilul tău de cumpărături</p>
          <h3>Preferințe curente</h3>
        </div>
      </div>

      <div className="profile-summary-grid">
        <div className="profile-summary-column">
          <div className="profile-summary-item">
            <span className="item-label">Grupa de vârstă</span>
            <span className="item-value">{profile.age_group}</span>
          </div>
          <div className="profile-summary-item">
            <span className="item-label">Buget</span>
            <span className="item-value">{BUDGET_LABELS[profile.budget_range] || profile.budget_range}</span>
          </div>
        </div>
        <div className="profile-summary-column details-column">
          <div className="profile-pill-group">
            <span className="item-label">Interese</span>
            <div className="pill-wrapper">
              {interests.length === 0 && <span className="item-value muted">Nu ai selectat interese</span>}
              {interests.map((interest) => (
                <span key={interest} className="profile-pill">
                  <Smartphone className="pill-icon" />
                  {formatInterestLabel(interest)}
                </span>
              ))}
            </div>
          </div>
          <div className="profile-pill-group">
            <span className="item-label">Branduri preferate</span>
            <div className="pill-wrapper">
              {preferredBrands.length === 0 && <span className="item-value muted">Nu ai selectat branduri</span>}
              {preferredBrands.map((brand) => (
                <span key={brand} className="profile-pill brand-pill">
                  <Star className="pill-icon" />
                  {brand}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Login Page
const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("login");
  const [regAge, setRegAge] = useState("18-25");
  const [regBudget, setRegBudget] = useState("medium");
  const [regInterests, setRegInterests] = useState(["laptops"]);
  const [regBrands, setRegBrands] = useState("");

  const isRegister = mode === "register";

  const toggleRegInterest = (value) => {
    setRegInterests((prev) =>
      prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value]
    );
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRegister) {
        if (regInterests.length === 0) {
          toast.error("Selectează cel puțin un interes");
          setLoading(false);
          return;
        }
        const response = await axios.post(`${API}/auth/register`, {
          username,
          password,
          age_group: regAge,
          budget_range: regBudget,
          interests: regInterests,
          preferred_brands: parseListInput(regBrands),
        });
        onLogin(response.data);
        toast.success("Cont creat şi autentificat!");
      } else {
        const response = await axios.post(`${API}/auth/login`, {
          username,
          password,
        });
        onLogin(response.data);
        toast.success(`Bun venit, ${response.data.username}!`);
      }
    } catch (error) {
      const detail = error.response?.data?.detail || "Autentificare eșuată. Verifică datele introduse.";
      toast.error(detail);
      console.error("Auth error:", error);
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
              {isRegister && (
                <>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Grupă de vârstă</label>
                      <select className="auth-select" value={regAge} onChange={(e) => setRegAge(e.target.value)}>
                        <option value="18-25">18-25</option>
                        <option value="26-35">26-35</option>
                        <option value="36-50">36-50</option>
                        <option value="50+">50+</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Buget</label>
                      <select className="auth-select" value={regBudget} onChange={(e) => setRegBudget(e.target.value)}>
                        <option value="low">Buget redus (&lt;500 RON)</option>
                        <option value="medium">Buget mediu (500-1200 RON)</option>
                        <option value="high">Buget ridicat (&gt;1200 RON)</option>
                      </select>
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Interese</label>
                    <div className="interest-grid">
                      {INTEREST_OPTIONS.map((option) => (
                        <button
                          type="button"
                          key={`register-${option.value}`}
                          className={`interest-chip ${regInterests.includes(option.value) ? "active" : ""}`}
                          onClick={() => toggleRegInterest(option.value)}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Branduri preferate (separate prin virgulă)</label>
                    <Input
                      className="auth-input"
                      value={regBrands}
                      placeholder="Apple, Samsung"
                      onChange={(e) => setRegBrands(e.target.value)}
                    />
                  </div>
                </>
              )}
              <Button
                data-testid="login-button"
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading ? "Se încarcă..." : isRegister ? "Creează cont" : "Autentificare"}
              </Button>
            </form>
            <div className="auth-toggle">
              {isRegister ? "Ai deja cont?" : "Nu ai cont?"}{" "}
              <button type="button" onClick={() => setMode(isRegister ? "login" : "register")}>
                {isRegister ? "Autentifică-te" : "Creează unul"}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Product Card Component
const ProductCard = ({ product, onClick, isRecommended = false, onAddToCart, matchInfo, isFavorite = false, onToggleFavorite }) => {
  const isAvailable = (product.stock ?? 0) > 0 && product.is_active !== false;
  const tags = product.tags && product.tags.length ? product.tags : [product.category];
  const handleAddToCart = (e) => {
    e.stopPropagation();
    onAddToCart(product);
  };
  
  const handleToggleFavorite = (e) => {
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(product.id);
    }
  };

  const matchScore = typeof matchInfo?.score === "number" ? Math.round(matchInfo.score) : null;

  return (
    <Card 
      className="product-card" 
      onClick={onClick}
      data-testid={`product-card-${product.id}`}
    >
      {isRecommended && (
        <div className="recommended-badge">
          <Star className="w-3 h-3" />
          <span>{matchScore !== null ? `${matchScore}% potrivire` : "Recomandat"}</span>
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
        {onToggleFavorite && (
          <Button
            variant="ghost"
            size="sm"
            className="favorite-btn"
            onClick={handleToggleFavorite}
            data-testid={`favorite-btn-${product.id}`}
          >
            <Heart className={`w-4 h-4 ${isFavorite ? "fill-red-500 text-red-500" : ""}`} />
          </Button>
        )}
      </div>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="product-name">{product.name}</CardTitle>
          <Badge className="brand-badge">{product.brand}</Badge>
        </div>
        <CardDescription className="product-description">
          {product.description}
        </CardDescription>
        <div className="product-tags">
          {tags.map((tag) => (
            <span key={`${product.id}-tag-${tag}`} className="product-tag-chip">
              {tag}
            </span>
          ))}
        </div>
      </CardHeader>
      <CardFooter className="product-footer">
        <div>
          <div className="price-tag">{product.price.toFixed(2)} RON</div>
          {product.stock !== undefined && (
            <div className="stock-info">
              <Package className="w-3 h-3" />
              <span className={isAvailable ? "in-stock" : "out-of-stock"}>
                {isAvailable ? `În stoc: ${product.stock}` : "Momentan indisponibil"}
              </span>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button 
            className="add-to-cart-mini-btn" 
            onClick={handleAddToCart}
            data-testid={`add-to-cart-${product.id}`}
            disabled={!isAvailable}
          >
            <ShoppingCart className="w-4 h-4" />
          </Button>
          <Button className="view-details-btn" data-testid={`view-product-${product.id}`}>
            Detalii
          </Button>
        </div>
      </CardFooter>
      {matchInfo && (
        <div className="match-details" data-testid={`match-details-${product.id}`}>
          {matchScore !== null && (
            <div className="match-score-row">
              <Zap className="match-score-icon" />
              <div>
                <p>Potrivire generală</p>
                <strong>{matchScore}%</strong>
              </div>
            </div>
          )}
          <div className="match-tags">
            {matchInfo?.breakdown?.interest && (
              <span className={`match-tag ${matchInfo.breakdown.interest.match ? "positive" : "neutral"}`}>
                {matchInfo.breakdown.interest.label}
              </span>
            )}
            {matchInfo?.breakdown?.brand && (
              <span className={`match-tag ${matchInfo.breakdown.brand.match ? "positive" : "neutral"}`}>
                {matchInfo.breakdown.brand.label}
              </span>
            )}
            {matchInfo?.breakdown?.budget && (
              <span className={`match-tag ${matchInfo.breakdown.budget.match ? "positive" : "neutral"}`}>
                {matchInfo.breakdown.budget.detail}
              </span>
            )}
          </div>
          {matchInfo.match_reasons?.length > 0 && (
            <ul className="match-reasons">
              {matchInfo.match_reasons.slice(0, 3).map((reason, index) => (
                <li key={`${product.id}-reason-${index}`}>{reason}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Card>
  );
};

const AdminPanel = ({ user, onRefresh }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    category: "",
    brand: "",
    price: 0,
    description: "",
    image_url: "",
    specs: {},
    stock: 0,
    supplier: "",
    delivery_method: "",
    is_active: true
  });
  const [imagePreview, setImagePreview] = useState("");

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/products`, { params: { active_only: false } });
      setProducts(response.data);
    } catch (error) {
      toast.error("Eroare la încărcarea produselor");
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const getAdminHeaders = () => ({
    "X-User-Id": user.user_id,
    "X-User-Role": user.role
  });

  const handleDelete = async (productId) => {
    if (!window.confirm("Ești sigur că vrei să ștergi acest produs?")) return;
    
    try {
      await axios.delete(`${API}/products/${productId}`, { headers: getAdminHeaders() });
      toast.success("Produs șters cu succes");
      fetchProducts();
      if (onRefresh) onRefresh();
    } catch (error) {
      toast.error("Eroare la ștergerea produsului");
      console.error("Delete error:", error);
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      category: product.category,
      brand: product.brand,
      price: product.price,
      description: product.description,
      image_url: product.image_url,
      specs: product.specs || {},
      stock: product.stock || 0,
      supplier: product.supplier || "",
      delivery_method: product.delivery_method || "",
      is_active: product.is_active ?? product.stock > 0
    });
    setImagePreview(product.image_url || "");
    setShowAddForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        is_active: formData.stock > 0 ? formData.is_active : false,
      };

      if (editingProduct) {
        await axios.put(`${API}/products/${editingProduct.id}`, payload, { headers: getAdminHeaders() });
        toast.success("Produs actualizat cu succes");
      } else {
        await axios.post(`${API}/products`, payload, { headers: getAdminHeaders() });
        toast.success("Produs adăugat cu succes");
      }
      setShowAddForm(false);
      setEditingProduct(null);
      setFormData({
        name: "", category: "", brand: "", price: 0, description: "",
        image_url: "", specs: {}, stock: 0, supplier: "", delivery_method: "", is_active: true
      });
      setImagePreview("");
      fetchProducts();
      if (onRefresh) onRefresh();
    } catch (error) {
      toast.error(editingProduct ? "Eroare la actualizarea produsului" : "Eroare la adăugarea produsului");
      console.error("Submit error:", error);
    }
  };

  const handleProductImageUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = reader.result?.toString() || "";
      setImagePreview(dataUrl);
      setFormData({ ...formData, image_url: dataUrl });
      toast.success("Imagine produs încărcată cu succes");
    };
    reader.onerror = () => {
      toast.error("Nu am putut încărca imaginea");
    };
    reader.readAsDataURL(file);
  };

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div><p>Se încarcă...</p></div>;
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>Gestionare Produse</h2>
        <Button className="btn-glow" onClick={() => { setShowAddForm(true); setEditingProduct(null); }}>
          <Plus className="w-4 h-4 mr-2" />
          Adaugă Produs
        </Button>
      </div>

      {showAddForm && (
        <Card className="admin-form-card">
          <CardHeader>
            <CardTitle className="card-title-contrast">{editingProduct ? "Editează Produs" : "Adaugă Produs Nou"}</CardTitle>
            <CardDescription className="card-description-contrast">
              Completează detaliile produsului și salvează pentru a-l face disponibil utilizatorilor.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="admin-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Nume</label>
                  <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Categorie</label>
                  <Input value={formData.category} onChange={(e) => setFormData({...formData, category: e.target.value})} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Brand</label>
                  <Input value={formData.brand} onChange={(e) => setFormData({...formData, brand: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Preț (RON)</label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        price: parseFloat(e.target.value) || 0,
                      })
                    }
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Descriere</label>
                <textarea className="form-textarea" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>URL Imagine</label>
                <Input value={formData.image_url} onChange={(e) => setFormData({...formData, image_url: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Imagine locală</label>
                <div className="avatar-actions">
                  <label className="upload-label">
                    <Camera className="w-4 h-4" />
                    Încarcă fișier
                    <input type="file" accept="image/*" onChange={handleProductImageUpload} />
                  </label>
                  {imagePreview && (
                    <img src={imagePreview} alt="Preview produs" className="product-preview-thumb" />
                  )}
                </div>
                <p className="form-hint">Poți folosi fie un link extern, fie o imagine locală.</p>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Stoc</label>
                  <Input
                    type="number"
                    value={formData.stock}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        stock: parseInt(e.target.value, 10) || 0,
                      })
                    }
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Furnizor</label>
                  <Input value={formData.supplier} onChange={(e) => setFormData({...formData, supplier: e.target.value})} required />
                </div>
              </div>
              <div className="form-group">
                <label>Modalitate de livrare</label>
                <Input value={formData.delivery_method} onChange={(e) => setFormData({...formData, delivery_method: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Status produs</label>
                <label
                  className={`status-switch ${formData.is_active ? "on" : "off"} ${
                    formData.stock <= 0 ? "disabled" : ""
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    disabled={formData.stock <= 0}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  <span>{formData.is_active ? "Activ" : "Inactiv"}</span>
                </label>
                {formData.stock <= 0 && (
                  <p className="form-hint">Adaugă stoc pentru a activa din nou produsul.</p>
                )}
              </div>
              <div className="form-group">
                <label>Specificații</label>
                <textarea className="form-textarea" value={JSON.stringify(formData.specs, null, 2)} onChange={(e) => {
                  try {
                    setFormData({...formData, specs: JSON.parse(e.target.value)});
                  } catch {}
                }} placeholder='{"processor": "Intel i7", "ram": "16GB"}' />
              </div>
              <div className="form-actions">
                <Button type="submit" className="btn-glow">{editingProduct ? "Actualizează" : "Adaugă"}</Button>
                <Button type="button" variant="outline" className="btn-outline-neutral" onClick={() => { setShowAddForm(false); setEditingProduct(null); }}>Anulează</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="admin-products-list">
        {products.map(product => (
          <Card key={product.id} className="admin-product-card">
            <CardContent className="admin-product-content">
              <div className="admin-product-info">
                <img src={product.image_url} alt={product.name} className="admin-product-image" />
                <div>
                  <h3>{product.name}</h3>
                  <p>{product.brand} - {product.category}</p>
                  <p>Preț: {product.price.toFixed(2)} RON | Stoc: {product.stock}</p>
                  <span className={`status-chip ${product.is_active ? "active" : "inactive"}`}>
                    {product.is_active ? "Activ" : "Inactiv"}
                  </span>
                </div>
              </div>
              <div className="admin-product-actions">
                <Button variant="outline" size="sm" className="admin-action-btn" onClick={() => handleEdit(product)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="destructive" size="sm" className="admin-delete-btn" onClick={() => handleDelete(product.id)}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

const Dashboard = ({ user, onLogout, cart, setCart }) => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [initialLoading, setInitialLoading] = useState(true);
  const [productsLoading, setProductsLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [recommendationReason, setRecommendationReason] = useState("");
  const [cartOpen, setCartOpen] = useState(false);
  const [profileData, setProfileData] = useState(user?.profile ?? null);
  const [favorites, setFavorites] = useState([]);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [checkoutData, setCheckoutData] = useState({
    full_name: "",
    address: "",
    city: "",
    postal_code: "",
    phone: "",
    email: "",
    payment_method: "card"
  });

  useEffect(() => {
    fetchDashboardData();
    fetchFavorites();
  }, [user]);

  const fetchFavorites = async () => {
    try {
      const response = await axios.get(`${API}/favorites/${user.user_id}`);
      setFavorites(response.data.map(p => p.id));
    } catch (error) {
      console.error("Error fetching favorites:", error);
    }
  };

  const toggleFavorite = async (productId) => {
    try {
      const isFavorite = favorites.includes(productId);
      if (isFavorite) {
        await axios.delete(`${API}/favorites/${user.user_id}/${productId}`);
        setFavorites(favorites.filter(id => id !== productId));
        toast.success("Produs eliminat din favorite");
      } else {
        await axios.post(`${API}/favorites/${user.user_id}/${productId}`);
        setFavorites([...favorites, productId]);
        toast.success("Produs adăugat la favorite");
      }
    } catch (error) {
      toast.error("Eroare la actualizarea favorite");
      console.error("Favorite error:", error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setInitialLoading(true);
      const [recResponse, productsResponse, categoriesResponse] = await Promise.all([
        axios.get(`${API}/recommendations/${user.user_id}`),
        axios.get(`${API}/products`, { params: { active_only: true } }),
        axios.get(`${API}/categories`, { params: { active_only: true } }),
      ]);

      const matches = recResponse.data.product_matches?.length
        ? recResponse.data.product_matches
        : recResponse.data.products.map((product) => ({
            product,
            score: null,
            breakdown: null,
            match_reasons: [],
          }));
      setRecommendations(matches);
      setRecommendationReason(recResponse.data.reason);
      const serverProfile = recResponse.data.user_profile ?? user.profile;
      const mergedProfile = { ...serverProfile, ...(user.profile || {}) };
      setProfileData(mergedProfile);
      setAllProducts(productsResponse.data);
      setCategories(categoriesResponse.data);
      setInitialized(true);
      if (selectedCategory) {
        await fetchProductsByCategory(selectedCategory);
      }
    } catch (error) {
      toast.error("Eroare la încărcarea produselor");
      console.error("Fetch error:", error);
    } finally {
      setInitialLoading(false);
    }
  };

  const fetchProductsByCategory = async (category) => {
    try {
      setProductsLoading(true);
      const response = await axios.get(`${API}/products`, {
        params: {
          category: category || undefined,
          active_only: true,
        },
      });
      setAllProducts(response.data);
    } catch (error) {
      toast.error("Nu am putut filtra produsele.");
      console.error("Filter error:", error);
    } finally {
      setProductsLoading(false);
    }
  };

  const handleCategoryChange = (category) => {
    if (!initialized) return;
    if (category === selectedCategory) return;
    setSelectedCategory(category);
    fetchProductsByCategory(category);
  };

  const handleProductClick = (productId) => {
    navigate(`/product/${productId}`);
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (product.stock === 0) {
      toast.error("Produs indisponibil");
      return;
    }
    
    if (existingItem) {
      if (existingItem.quantity >= product.stock) {
        toast.error("Stoc insuficient");
        return;
      }
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
        if (delta > 0 && newQuantity > item.stock) {
          toast.error("Stoc insuficient");
          return item;
        }
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

  const handleCheckout = async () => {
    if (cart.length === 0) {
      toast.error("Coșul este gol");
      return;
    }
    setCheckoutOpen(true);
  };

  const submitCheckout = async () => {
    if (!checkoutData.full_name || !checkoutData.address || !checkoutData.city || !checkoutData.phone || !checkoutData.email) {
      toast.error("Completează toate câmpurile obligatorii");
      return;
    }
    try {
      await axios.post(`${API}/transactions`, {
        items: cart.map((item) => ({
          product_id: item.id,
          quantity: item.quantity,
        })),
        shipping_address: checkoutData.address,
        city: checkoutData.city,
        postal_code: checkoutData.postal_code,
        full_name: checkoutData.full_name,
        phone: checkoutData.phone,
        email: checkoutData.email,
        payment_method: checkoutData.payment_method
      }, {
        headers: {
          "X-User-Id": user.user_id
        }
      });
      toast.success("Comandă procesată cu succes!");
      setCart([]);
      setCartOpen(false);
      setCheckoutOpen(false);
      setCheckoutData({
        full_name: "",
        address: "",
        city: "",
        postal_code: "",
        phone: "",
        email: "",
        payment_method: "card"
      });
      await fetchDashboardData();
      await fetchProductsByCategory(selectedCategory);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Nu am putut procesa tranzacția");
    }
  };

  if (initialLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Se încarcă...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container" data-testid="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section">
            <Zap className="header-logo" />
            <h1 className="header-title">TechStore</h1>
          </div>
          <div className="user-section">
            <button
              type="button"
              className="user-info"
              onClick={() => navigate("/profile")}
              data-testid="profile-trigger"
            >
              {user.profileImage ? (
                <img src={user.profileImage} alt={user.username} className="user-avatar" />
              ) : (
                <User className="user-icon" />
              )}
              <span className="user-name" data-testid="user-name">{user.username}</span>
              {user.role === "admin" && (
                <Badge variant="secondary" className="role-badge">Admin</Badge>
              )}
            </button>
            
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

            <Dialog open={checkoutOpen} onOpenChange={setCheckoutOpen}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Finalizare comandă</DialogTitle>
                  <DialogDescription>
                    Completează datele de livrare pentru comanda ta
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Nume complet *</label>
                    <Input
                      value={checkoutData.full_name}
                      onChange={(e) => setCheckoutData({...checkoutData, full_name: e.target.value})}
                      placeholder="Ion Popescu"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Adresă *</label>
                    <Input
                      value={checkoutData.address}
                      onChange={(e) => setCheckoutData({...checkoutData, address: e.target.value})}
                      placeholder="Strada Exemplu, Nr. 1"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <label className="text-sm font-medium">Oraș *</label>
                      <Input
                        value={checkoutData.city}
                        onChange={(e) => setCheckoutData({...checkoutData, city: e.target.value})}
                        placeholder="București"
                        required
                      />
                    </div>
                    <div className="grid gap-2">
                      <label className="text-sm font-medium">Cod poștal</label>
                      <Input
                        value={checkoutData.postal_code}
                        onChange={(e) => setCheckoutData({...checkoutData, postal_code: e.target.value})}
                        placeholder="123456"
                      />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Telefon *</label>
                    <Input
                      type="tel"
                      value={checkoutData.phone}
                      onChange={(e) => setCheckoutData({...checkoutData, phone: e.target.value})}
                      placeholder="0712345678"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Email *</label>
                    <Input
                      type="email"
                      value={checkoutData.email}
                      onChange={(e) => setCheckoutData({...checkoutData, email: e.target.value})}
                      placeholder="exemplu@email.com"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Metodă de plată</label>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={checkoutData.payment_method}
                      onChange={(e) => setCheckoutData({...checkoutData, payment_method: e.target.value})}
                    >
                      <option value="card">Card bancar</option>
                      <option value="cash">Ramburs la livrare</option>
                    </select>
                  </div>
                  <div className="border-t pt-4">
                    <div className="flex justify-between text-lg font-semibold">
                      <span>Total:</span>
                      <span>{getTotalPrice().toFixed(2)} RON</span>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCheckoutOpen(false)}>
                    Anulează
                  </Button>
                  <Button onClick={submitCheckout}>
                    <Check className="w-4 h-4 mr-2" />
                    Confirmă comanda
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/orders")}
              className="logout-btn"
            >
              <History className="w-4 h-4" />
              Comenzile mele
            </Button>
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

      <main className="dashboard-main">
        <Tabs defaultValue="recommendations" className="dashboard-tabs">
          <TabsList className="tabs-list">
            <TabsTrigger value="recommendations" data-testid="recommendations-tab">Pentru Tine</TabsTrigger>
            <TabsTrigger value="all" data-testid="all-products-tab">Toate Produsele</TabsTrigger>
            <TabsTrigger value="favorites" data-testid="favorites-tab">
              <Heart className="w-4 h-4 mr-2" />
              Favorite
            </TabsTrigger>
            {user.role === "admin" && (
              <TabsTrigger value="admin" data-testid="admin-tab">
                <Settings className="w-4 h-4 mr-2" />
                Admin
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="recommendations" className="tab-content">
            <div className="recommendations-section">
              <div className="section-header">
                <h2 className="section-title">Recomandări Personalizate</h2>
                <p className="section-description" data-testid="recommendation-reason">{recommendationReason}</p>
              </div>
              <ProfileSummary profile={profileData ?? user.profile} profileImage={user.profileImage} />
              <div className="products-grid" data-testid="recommendations-grid">
                {recommendations.length === 0 ? (
                  <div className="empty-state">
                    Nu am găsit produse care să se potrivească preferințelor tale actuale. Actualizează interesele din pagina de profil.
                  </div>
                ) : (
                  recommendations.map((match) => (
                    <ProductCard
                      key={match.product.id}
                      product={match.product}
                      matchInfo={match.score !== null ? match : null}
                      onClick={() => handleProductClick(match.product.id)}
                      onAddToCart={addToCart}
                      isRecommended={true}
                      isFavorite={favorites.includes(match.product.id)}
                      onToggleFavorite={toggleFavorite}
                    />
                  ))
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="all" className="tab-content">
            <div className="all-products-section">
              <div className="section-header">
                <h2 className="section-title">Toate Produsele</h2>
                <p className="section-description">Explorează întreaga noastră colecție</p>
              </div>
                <div className="categories-filter">
                <Button
                  className={`filter-chip ${selectedCategory === null ? "active" : ""}`}
                  onClick={() => handleCategoryChange(null)}
                >
                  Toate
                </Button>
                {categories.map(cat => (
                  <Button
                    key={cat}
                    className={`filter-chip ${selectedCategory === cat ? "active" : ""}`}
                    onClick={() => handleCategoryChange(cat)}
                  >
                    {cat}
                  </Button>
                ))}
              </div>
                <div className="search-wrapper">
                  <Input
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Caută produs după nume..."
                    className="search-input"
                  />
                </div>
              {productsLoading ? (
                <div className="products-loading">
                  <div className="spinner small"></div>
                  <p>Actualizăm lista de produse...</p>
                </div>
              ) : (
                <div className="products-grid" data-testid="all-products-grid">
                  {allProducts
                    .filter((product) =>
                      product.name.toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .map((product) => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onClick={() => handleProductClick(product.id)}
                      onAddToCart={addToCart}
                      isFavorite={favorites.includes(product.id)}
                      onToggleFavorite={toggleFavorite}
                    />
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="favorites" className="tab-content">
            <div className="all-products-section">
              <div className="section-header">
                <h2 className="section-title">Produse favorite</h2>
                <p className="section-description">Produsele tale favorite</p>
              </div>
              {productsLoading ? (
                <div className="products-loading">
                  <div className="spinner small"></div>
                  <p>Se încarcă...</p>
                </div>
              ) : (
                <div className="products-grid">
                  {allProducts
                    .filter(product => favorites.includes(product.id))
                    .map((product) => (
                      <ProductCard
                        key={product.id}
                        product={product}
                        onClick={() => handleProductClick(product.id)}
                        onAddToCart={addToCart}
                        isFavorite={true}
                        onToggleFavorite={toggleFavorite}
                      />
                    ))}
                  {allProducts.filter(product => favorites.includes(product.id)).length === 0 && (
                    <div className="empty-state">
                      Nu ai produse în lista de favorite. Adaugă produse la favorite pentru a le accesa mai ușor.
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          {user.role === "admin" && (
            <TabsContent value="admin" className="tab-content">
              <AdminPanel user={user} onRefresh={fetchDashboardData} />
            </TabsContent>
          )}
        </Tabs>
      </main>
    </div>
  );
};

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
    if (product.stock === 0) {
      toast.error("Produs indisponibil");
      return;
    }
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      if (existingItem.quantity >= product.stock) {
        toast.error("Stoc insuficient");
        return;
      }
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
  const detailTags = product.tags && product.tags.length ? product.tags : [product.category];

  const isAvailable = product.stock > 0 && product.is_active !== false;

  return (
    <div className="product-details-container" data-testid="product-details">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section" onClick={() => navigate("/dashboard")} style={{ cursor: "pointer" }}>
            <Zap className="header-logo" />
            <h1 className="header-title">TechStore</h1>
          </div>
          <div className="user-section">
            <button
              type="button"
              className="user-info"
              onClick={() => navigate("/profile")}
            >
              {user.profileImage ? (
                <img src={user.profileImage} alt={user.username} className="user-avatar" />
              ) : (
                <User className="user-icon" />
              )}
              <span className="user-name">{user.username}</span>
              {user.role === "admin" && (
                <Badge variant="secondary" className="role-badge">Admin</Badge>
              )}
            </button>
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
            <div className="detail-tags">
              {detailTags.map((tag) => (
                <span key={`detail-tag-${tag}`} className="product-tag-chip">
                  {tag}
                </span>
              ))}
            </div>
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

            <div className="product-info-section">
              <div className="info-row">
                <div className="info-item">
                  <span className="info-label">Stoc:</span>
                  <span className={`info-value ${product.stock > 0 ? "in-stock" : "out-of-stock"}`}>
                    {product.stock !== undefined ? (product.stock > 0 ? `${product.stock} bucăți` : "Stoc epuizat") : "N/A"}
                  </span>
                </div>
                {product.supplier && (
                  <div className="info-item">
                    <span className="info-label">Furnizor:</span>
                    <span className="info-value">{product.supplier}</span>
                  </div>
                )}
                {product.delivery_method && (
                  <div className="info-item">
                    <span className="info-label">Livrare:</span>
                    <span className="info-value">{product.delivery_method}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="price-section">
              <div className="price-large" data-testid="product-price">{product.price.toFixed(2)} RON</div>
              <Button 
                className="add-to-cart-btn" 
                onClick={addToCart}
                data-testid="add-to-cart-button"
                disabled={!isAvailable}
              >
                <ShoppingCart className="w-5 h-5" />
                {isAvailable ? "Adaugă în coș" : "Indisponibil"}
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const OrderHistoryPage = ({ user }) => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, [user]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/orders/${user.user_id}`);
      setOrders(response.data);
    } catch (error) {
      toast.error("Eroare la încărcarea comenzilor");
      console.error("Orders error:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      pending: { label: "În așteptare", className: "bg-yellow-100 text-yellow-800" },
      confirmed: { label: "Confirmată", className: "bg-blue-100 text-blue-800" },
      shipped: { label: "Expediată", className: "bg-purple-100 text-purple-800" },
      delivered: { label: "Livrată", className: "bg-green-100 text-green-800" },
      cancelled: { label: "Anulată", className: "bg-red-100 text-red-800" },
    };
    const statusInfo = statusMap[status] || statusMap.pending;
    return <Badge className={statusInfo.className}>{statusInfo.label}</Badge>;
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString("ro-RO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Se încarcă comenzile...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section" onClick={() => navigate("/dashboard")} style={{ cursor: "pointer" }}>
            <Zap className="header-logo" />
            <h1 className="header-title">TechStore</h1>
          </div>
          <div className="user-section">
            <Button variant="outline" size="sm" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Înapoi
            </Button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="all-products-section">
          <div className="section-header">
            <h2 className="section-title">Istoric comenzi</h2>
            <p className="section-description">Toate comenzile tale</p>
          </div>
          
          {orders.length === 0 ? (
            <div className="empty-state">
              Nu ai comandat încă. Explorează produsele și începe să cumperi!
            </div>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => (
                <Card key={order.id} className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold">Comandă #{order.id.slice(0, 8)}</h3>
                      <p className="text-sm text-gray-500">{formatDate(order.created_at)}</p>
                    </div>
                    {getStatusBadge(order.status)}
                  </div>
                  
                  <div className="border-t pt-4 mb-4">
                    <h4 className="font-medium mb-2">Produse:</h4>
                    <div className="space-y-2">
                      {order.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between text-sm">
                          <span>{item.product_name} x {item.quantity}</span>
                          <span>{(item.price * item.quantity).toFixed(2)} RON</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {order.shipping_info && (
                    <div className="border-t pt-4 mb-4">
                      <h4 className="font-medium mb-2">Date livrare:</h4>
                      <div className="text-sm text-gray-600">
                        {order.shipping_info.address && <p>{order.shipping_info.address}</p>}
                        {order.shipping_info.phone && <p>Tel: {order.shipping_info.phone}</p>}
                        {order.shipping_info.email && <p>Email: {order.shipping_info.email}</p>}
                      </div>
                    </div>
                  )}

                  <div className="border-t pt-4 flex justify-between items-center">
                    <span className="font-semibold">Total:</span>
                    <span className="text-xl font-bold">{order.total_amount.toFixed(2)} RON</span>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

const ProfilePage = ({ user, setUser }) => {
  const navigate = useNavigate();
  const [profileImage, setProfileImage] = useState(user.profileImage || "");
  const [ageGroup, setAgeGroup] = useState(user.profile.age_group || "18-25");
  const [budgetRange, setBudgetRange] = useState(user.profile.budget_range || "medium");
  const normalizeInterests = (interests) => {
    if (Array.isArray(interests)) return interests;
    if (!interests) return [];
    return parseListInput(interests);
  };
  const [selectedInterests, setSelectedInterests] = useState(() => normalizeInterests(user.profile.interests));
  const [brandsInput, setBrandsInput] = useState(formatListInput(user.profile.preferred_brands));
  const [saving, setSaving] = useState(false);
  const [usernameInput, setUsernameInput] = useState(user.username);
  const [usernameError, setUsernameError] = useState("");
  const customInterestOptions = selectedInterests
    .filter((interest) => !INTEREST_LABELS[interest])
    .map((interest) => ({
      value: interest,
      label: interest.charAt(0).toUpperCase() + interest.slice(1),
    }));
  const interestOptions = [...INTEREST_OPTIONS, ...customInterestOptions].filter(
    (option, index, self) => self.findIndex((o) => o.value === option.value) === index
  );

  const handleImageUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const raw = await readFileAsDataUrl(file);
      const processed = await compressImageDataUrl(raw);
      setProfileImage(processed);
      toast.success("Poză actualizată");
    } catch (error) {
      console.error("Avatar upload error:", error);
      toast.error("Nu am putut procesa imaginea");
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setUsernameError("");
    setSaving(true);
    if (selectedInterests.length === 0) {
      toast.error("Selectează cel puțin o categorie de interes");
      setSaving(false);
      return;
    }
    const normalizedUsername = usernameInput.trim();
    if (!normalizedUsername) {
      setUsernameError("Username-ul nu poate fi gol");
      setSaving(false);
      return;
    }
    const preparedBrands = parseListInput(brandsInput);
    const updatedProfile = {
      age_group: ageGroup,
      budget_range: budgetRange,
      interests: selectedInterests,
      preferred_brands: preparedBrands,
    };
    const payload = {
      ...updatedProfile,
      username: normalizedUsername,
    };

    try {
      await axios.put(`${API}/profile/${user.user_id}`, payload);
      const updatedUser = {
        ...user,
        username: normalizedUsername,
        profile: {
          ...user.profile,
          ...updatedProfile,
        },
        profileImage,
      };

      setUser(updatedUser);
      safeSetItem("user", JSON.stringify(updatedUser));
      saveProfileOverrides(user.user_id, {
        profileImage,
        profile: updatedProfile,
      });

      toast.success("Profil actualizat cu succes!");
      navigate("/dashboard");
    } catch (error) {
      const detail = error.response?.data?.detail || "Nu am putut salva profilul";
      if (detail.toLowerCase().includes("username")) {
        setUsernameError(detail);
      }
      toast.error(detail);
    } finally {
      setSaving(false);
    }
  };

  const toggleInterest = (interest) => {
    setSelectedInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((item) => item !== interest)
        : [...prev, interest]
    );
  };

  const interestsPreview = selectedInterests;
  const brandsPreview = parseListInput(brandsInput);

  return (
    <div className="profile-page">
      <header className="profile-header">
        <Button variant="ghost" className="back-link" onClick={() => navigate(-1)}>
          <ArrowLeft className="w-4 h-4" />
          Înapoi
        </Button>
        <h1 className="profile-page-title">Profilul meu</h1>
      </header>

      <div className="profile-content">
        <div className="profile-preview-card">
          <div className="profile-avatar-large">
            {profileImage ? (
              <img src={profileImage} alt="Profil" />
            ) : (
              <UserCircle className="w-16 h-16 text-slate-300" />
            )}
          </div>
          <h2>{usernameInput || user.username}</h2>
          <p className="profile-role-label">{user.role === "admin" ? "Administrator" : "Client"}</p>
          <div className="profile-chips">
            <span className="chip">{ageGroup}</span>
            <span className="chip">{BUDGET_LABELS[budgetRange] || budgetRange}</span>
          </div>
          <div className="profile-interests">
            <h3>Interese</h3>
            <div className="chip-group">
              {interestsPreview.length === 0 ? (
                <span className="chip muted">Adaugă interese</span>
              ) : (
                interestsPreview.map((item) => (
                  <span key={item} className="chip">
                    {INTEREST_LABELS[item] || item}
                  </span>
                ))
              )}
            </div>
          </div>
          <div className="profile-interests">
            <h3>Branduri preferate</h3>
            <div className="chip-group">
              {brandsPreview.length === 0 ? (
                <span className="chip muted">Adaugă branduri</span>
              ) : (
                brandsPreview.map((item) => (
                  <span key={item} className="chip">
                    {item}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>

        <Card className="profile-form-card">
          <CardHeader>
            <CardTitle className="card-title-contrast">Configurează-ți profilul</CardTitle>
            <CardDescription className="card-description-contrast">Personalizează-ți avatarul și preferințele.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="profile-form" onSubmit={handleSaveProfile}>
              <div className="form-group">
                <label>Poză de profil</label>
                <div className="avatar-actions">
                  <Button type="button" variant="outline" className="btn-outline-neutral" onClick={() => profileImage && setProfileImage("")}>
                    Șterge
                  </Button>
                  <label className="upload-label">
                    <Camera className="w-4 h-4" />
                    Încarcă din dispozitiv
                    <input type="file" accept="image/*" onChange={handleImageUpload} />
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>Username</label>
                <Input
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                  placeholder="ex: techlover"
                  className={usernameError ? "input-error" : ""}
                />
                {usernameError && <span className="error-text">{usernameError}</span>}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Grupa de vârstă</label>
                  <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)}>
                    <option value="18-25">18-25</option>
                    <option value="26-35">26-35</option>
                    <option value="36-50">36-50</option>
                    <option value="50+">50+</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Buget</label>
                  <select value={budgetRange} onChange={(e) => setBudgetRange(e.target.value)}>
                    <option value="low">Buget redus (&lt;500 RON)</option>
                    <option value="medium">Buget mediu (500-1200 RON)</option>
                    <option value="high">Buget ridicat (&gt;1200 RON)</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Interese</label>
                <p className="form-hint">Alege categoriile care te interesează</p>
                <div className="interest-grid">
                  {interestOptions.map((interest) => {
                    const active = selectedInterests.includes(interest.value);
                    return (
                      <button
                        type="button"
                        key={interest.value}
                        className={`interest-chip ${active ? "active" : ""}`}
                        onClick={() => toggleInterest(interest.value)}
                      >
                        {interest.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="form-group">
                <label>Branduri preferate (separate prin virgulă)</label>
                <Input
                  value={brandsInput}
                  placeholder="Apple, Samsung, Dell"
                  onChange={(e) => setBrandsInput(e.target.value)}
                />
              </div>

              <div className="profile-form-actions">
                <Button type="submit" disabled={saving} className="btn-glow">
                  <Save className="w-4 h-4 mr-2" />
                  {saving ? "Se salvează..." : "Salvează profilul"}
                </Button>
                <Button type="button" variant="ghost" className="btn-outline-neutral" onClick={() => navigate("/dashboard")}>
                  Renunță
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

function App() {
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState([]);

  const handleLogin = (userData) => {
    const enhancedUser = applyProfileOverrides(userData);
    setUser(enhancedUser);
    safeSetItem("user", JSON.stringify(enhancedUser));
  };

  const handleLogout = () => {
    setUser(null);
    setCart([]);
    safeRemoveItem("user");
    safeRemoveItem("cart");
    toast.info("Te-ai deconectat cu succes");
  };

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        const enhanced = applyProfileOverrides(parsed);
        setUser(enhanced);
        localStorage.setItem("user", JSON.stringify(enhanced));
      } catch {
        setUser(null);
      }
    }
    
    const savedCart = localStorage.getItem("cart");
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  }, []);

  useEffect(() => {
    if (cart.length > 0) {
      safeSetItem("cart", JSON.stringify(cart));
    } else {
      safeRemoveItem("cart");
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
          <Route
            path="/profile"
            element={
              user ? (
                <ProfilePage user={user} setUser={setUser} />
              ) : (
                <Navigate to="/" />
              )
            }
          />
          <Route
            path="/orders"
            element={
              user ? (
                <OrderHistoryPage user={user} />
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