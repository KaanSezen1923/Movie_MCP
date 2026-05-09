import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, SafeAreaView, ActivityIndicator, TouchableOpacity } from 'react-native';
import axios from 'axios';
import MovieCard from './Card'; // Mevcut Card bileşenini kullanıyoruz
import { Trash2 } from 'lucide-react-native';

const Watchlist = ({ userId }: { userId: number }) => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

// WatchList.tsx içi
  const fetchFavorites = async () => {
    try {
      // Eğer emülatör kullanıyorsan localhost yerine 10.0.2.2 (Android) 
      // ya da bilgisayarının yerel IP adresini kullanman gerekebilir.
      const res = await axios.get(`http://localhost:8000/favorites/${userId}`);
      
      // Backend'den dönen "favorites" dizisini state'e atıyoruz
      setFavorites(res.data.favorites || []); 
    } catch (e) {
      console.error("Favoriler yüklenemedi", e);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (movieId: string) => {
    try {
      // Backend'de bir DELETE endpoint'i olduğunu varsayıyoruz
      await axios.delete(`http://localhost:8000/favorites/${userId}/${movieId}`);
      setFavorites(prev => prev.filter(item => item.movie_id !== movieId));
    } catch (e) {
      console.error("Silme hatası", e);
    }
  };

  useEffect(() => { fetchFavorites(); }, []);

  if (loading) return <ActivityIndicator style={{flex:1}} color="#E50914" />;

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.header}>İzleme Listem</Text>
      <FlatList
        data={favorites}
        keyExtractor={(item) => item.movie_id}
        renderItem={({ item }) => (
          <View>
            <MovieCard movie={item} userId={userId} />
            <TouchableOpacity 
              style={styles.deleteButton} 
              onPress={() => removeFavorite(item.movie_id)}
            >
              <Trash2 color="#fff" size={18} />
              <Text style={styles.deleteText}>Listeden Çıkar</Text>
            </TouchableOpacity>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>Henüz film kaydetmediniz.</Text>}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', padding: 15 },
  header: { color: '#fff', fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  deleteButton: { flexDirection: 'row', backgroundColor: '#333', padding: 10, borderRadius: 8, marginTop: -15, marginBottom: 20, justifyContent: 'center', alignItems: 'center' },
  deleteText: { color: '#fff', marginLeft: 8, fontSize: 12 },
  empty: { color: '#999', textAlign: 'center', marginTop: 50 }
});

export default Watchlist;