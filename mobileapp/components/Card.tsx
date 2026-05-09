import React, { useState } from 'react';
import { 
  View, 
  Text, 
  Image, 
  StyleSheet, 
  TouchableOpacity, 
  Linking,
  Alert 
} from 'react-native';
import { Star, PlayCircle, Bookmark } from 'lucide-react-native';
import axios from 'axios';

// API URL'inizi buraya tanımlayın veya props olarak geçin
const API_BASE_URL = 'http://localhost:8000'; 

interface MovieData {
  Film?: string;
  Yıl?: string | number;
  "IMDb ★"?: string | number;
  IMDb?: string | number;
  "Tür(ler)"?: string;
  Türler?: string;
  "Kısa Özet"?: string;
  Özet?: string;
  Poster?: string;
  Fragman?: string;
  "Şu Anki Platform(lar)"?: string;
  // YENİ ALANLAR:
  Director?: string;
  Yönetmen?: string;
  Cast?: string;
  Oyuncular?: string;
}

// userId prop'u Chat.tsx'den gelmeli
const MovieCard = ({ movie, userId }: { movie: MovieData, userId: number }) => {
  const [isSaved, setIsSaved] = useState(false);

  // Veri Normalizasyonu
  const title = movie.Film || "Film Adı Bilinmiyor";
  const director = movie.Director  || "Bilinmiyor";
  const cast = movie.Cast  || "Bilinmiyor";
  const posterUrl = movie.Poster || "https://via.placeholder.com/500x750?text=No+Poster";

  const handleSaveFavorite = async () => {
    try {
      const payload = {
        user_id: userId,
        movie_id: title, // Benzersiz bir ID yoksa başlığı kullanıyoruz
        title: title,
        genres: movie.Türler || movie["Tür(ler)"],
        director: director,
        cast_members: cast,
        poster_url: posterUrl,
        imdb_rating: String(movie.IMDb || movie["IMDb ★"])
      };

      await axios.post(`${API_BASE_URL}/favorites`, payload);
      setIsSaved(true);
      Alert.alert("Başarılı", `${title} favorilerinize eklendi!`);
    } catch (error) {
      console.error("Favori hatası:", error);
      Alert.alert("Hata", "Favorilere eklenirken bir sorun oluştu.");
    }
  };

  return (
    <View style={styles.card}>
      <Image source={{ uri: posterUrl }} style={styles.poster} resizeMode="cover" />
      
      {/* Favori Butonu (Poster Üstünde Sağ Üstte) */}
      <TouchableOpacity 
        style={styles.saveIconContainer} 
        onPress={handleSaveFavorite}
      >
        <Bookmark 
          size={24} 
          color={isSaved ? "#E50914" : "#fff"} 
          fill={isSaved ? "#E50914" : "transparent"} 
        />
      </TouchableOpacity>

      <View style={styles.content}>
        <View style={styles.headerRow}>
          <Text style={styles.title} numberOfLines={1}>{title}</Text>
          <View style={styles.ratingBadge}>
            <Star size={14} color="#FFD700" fill="#FFD700" />
            <Text style={styles.ratingText}>{movie.IMDb || movie["IMDb ★"]}</Text>
          </View>
        </View>

        {/* Yeni Eklenen Bilgiler */}
        <Text style={styles.infoText}><Text style={styles.boldLabel}>Yönetmen:</Text> {director}</Text>
        <Text style={styles.infoText} numberOfLines={1}><Text style={styles.boldLabel}>Oyuncular:</Text> {cast}</Text>
        
        <Text style={styles.summary} numberOfLines={2}>{movie.Özet || movie["Kısa Özet"]}</Text>

        <View style={styles.footer}>
          <TouchableOpacity 
            style={styles.trailerButton} 
            onPress={() => movie.Fragman && Linking.openURL(movie.Fragman)}
          >
            <PlayCircle size={18} color="#fff" />
            <Text style={styles.trailerButtonText}>Fragman</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: { backgroundColor: '#1A1A1A', borderRadius: 15, marginBottom: 20, overflow: 'hidden', borderWidth: 0.5, borderColor: '#333' },
  poster: { width: '100%', height: 180 },
  saveIconContainer: { position: 'absolute', top: 10, right: 10, backgroundColor: 'rgba(0,0,0,0.5)', padding: 8, borderRadius: 20 },
  content: { padding: 12 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  title: { color: '#fff', fontSize: 18, fontWeight: 'bold', flex: 1 },
  ratingBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#333', padding: 4, borderRadius: 6 },
  ratingText: { color: '#FFD700', marginLeft: 4, fontWeight: 'bold' },
  infoText: { color: '#BBB', fontSize: 13, marginBottom: 2 },
  boldLabel: { color: '#E50914', fontWeight: 'bold' },
  summary: { color: '#999', fontSize: 13, marginTop: 8 },
  footer: { marginTop: 12, alignItems: 'flex-end' },
  trailerButton: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#E50914', padding: 8, borderRadius: 20 },
  trailerButtonText: { color: '#fff', fontWeight: 'bold', marginLeft: 5, fontSize: 12 }
});

export default MovieCard;