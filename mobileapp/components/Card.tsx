import React from 'react';
import { 
  View, 
  Text, 
  Image, 
  StyleSheet, 
  TouchableOpacity, 
  Linking 
} from 'react-native';
import { Star, PlayCircle, Info } from 'lucide-react-native';

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
  "Fragman (YouTube)"?: string;
  Fragman?: string;
  "İzleyebileceğin Platform(lar)"?: string;
  "Şu Anki Platform(lar)"?: string;
}

const MovieCard = ({ movie }: { movie: MovieData }) => {
  // Veritabanından gelen farklı anahtar isimlerini normalize ediyoruz
  const title = movie.Film || "Film Adı Bilinmiyor";
  const year = movie.Yıl || "";
  const rating = movie["IMDb ★"] || movie.IMDb || "N/A";
  const genres = movie["Tür(ler)"] || movie.Türler || "";
  const summary = movie["Kısa Özet"] || movie.Özet || "";
  const posterUrl = movie.Poster || "https://via.placeholder.com/500x750?text=No+Poster";
  const trailerUrl = movie["Fragman (YouTube)"] || movie.Fragman;
  const platforms = movie["İzleyebileceğin Platform(lar)"] || movie["Şu Anki Platform(lar)"];

  const handleOpenTrailer = () => {
    if (trailerUrl) {
      Linking.openURL(trailerUrl);
    }
  };

  return (
    <View style={styles.card}>
      {/* Film Posteri */}
      <Image source={{ uri: posterUrl }} style={styles.poster} resizeMode="cover" />
      
      <View style={styles.content}>
        {/* Başlık ve Yıl */}
        <View style={styles.headerRow}>
          <Text style={styles.title} numberOfLines={2}>
            {title} {year ? `(${year})` : ''}
          </Text>
          <View style={styles.ratingBadge}>
            <Star size={14} color="#FFD700" fill="#FFD700" />
            <Text style={styles.ratingText}>{rating}</Text>
          </View>
        </View>

        {/* Türler */}
        <Text style={styles.genres} numberOfLines={1}>{genres}</Text>

        {/* Özet */}
        <Text style={styles.summary} numberOfLines={3}>
          {summary}
        </Text>

        {/* Alt Bilgi: Platformlar ve Buton */}
        <View style={styles.footer}>
          <View style={styles.platformInfo}>
            <Text style={styles.platformLabel}>İzle:</Text>
            <Text style={styles.platformText} numberOfLines={1}>
              {platforms || "Bilgi Yok"}
            </Text>
          </View>

          {trailerUrl && (
            <TouchableOpacity style={styles.trailerButton} onPress={handleOpenTrailer}>
              <PlayCircle size={18} color="#fff" />
              <Text style={styles.trailerButtonText}>Fragman</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E1E1E', // Chat.tsx'deki header rengiyle uyumlu
    borderRadius: 12,
    marginBottom: 20,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#333',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  poster: {
    width: '100%',
    height: 200,
  },
  content: {
    padding: 15,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 5,
  },
  title: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
    marginRight: 10,
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#333',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  ratingText: {
    color: '#FFD700',
    fontWeight: 'bold',
    marginLeft: 4,
    fontSize: 14,
  },
  genres: {
    color: '#E50914', // Uygulamanızın ana kırmızı rengi
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 8,
  },
  summary: {
    color: '#CCC',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 15,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: '#333',
    paddingTop: 12,
  },
  platformInfo: {
    flex: 1,
    marginRight: 10,
  },
  platformLabel: {
    color: '#999',
    fontSize: 11,
    textTransform: 'uppercase',
  },
  platformText: {
    color: '#fff',
    fontSize: 12,
  },
  trailerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E50914',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
  },
  trailerButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
    marginLeft: 6,
  },
});

export default MovieCard;