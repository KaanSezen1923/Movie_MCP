import React, { useState, useEffect, useRef } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  FlatList, 
  StyleSheet, 
  SafeAreaView, 
  KeyboardAvoidingView, 
  Platform, 
  ActivityIndicator,
  Keyboard,
  StatusBar
} from 'react-native';
import { Send, Menu, Film } from 'lucide-react-native';
import axios from 'axios';
import MovieCard from './Card';

const API_BASE_URL = 'http://localhost:8000';

const Chat = ({ navigation, userId, sessionId, messages, setMessages, fetchSessions }: any) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // Başlık yüksekliğini manuel offset olarak ekliyoruz (Android çakışmasını önler)
  const headerHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 0 : 0;

useEffect(() => {
  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/chat/${userId}/${sessionId}`);
      
      const history = res.data.history.map((m: any) => {
        let finalContent = m.content;
        let extractedMovies = [];

        // Eğer içerik bir JSON string ise (filmleri ve metni içeren yapı)
        if (typeof m.content === 'string' && (m.content.startsWith('{') || m.content.startsWith('['))) {
          try {
            const parsed = JSON.parse(m.content);
            if (parsed.type === "movie_list") {
              finalContent = parsed.text;
              extractedMovies = parsed.movies;
            } else if (Array.isArray(parsed)) {
              // Eğer direkt film listesi gelmişse (eski kayıtlar için koruma)
              extractedMovies = parsed;
              finalContent = ""; 
            }
          } catch (e) {
            // JSON değilse olduğu gibi bırak
            finalContent = m.content;
          }
        }

        return {
          role: m.role,
          content: finalContent,
          // Eğer veritabanında ayrı bir 'movies' sütunu varsa m.movies'i kullan, 
          // yoksa yukarıda parse ettiğimiz extractedMovies'i kullan.
          movies: m.movies ? (typeof m.movies === 'string' ? JSON.parse(m.movies) : m.movies) : extractedMovies
        };
      });

      setMessages(history);
    } catch (e) {
      console.error("Geçmiş yükleme hatası:", e);
      setMessages([]);
    }
  };
  loadHistory();
}, [sessionId]);
const handleSend = async () => {
  if (!input.trim() || loading) return;
  const userMsg = { role: 'user', content: input };
  setMessages((prev: any) => [...prev, userMsg]);
  setInput('');
  setLoading(true);

  try {
    const res = await axios.post(`${API_BASE_URL}/chat`, {
      user_id: userId,
      session_id: sessionId,
      prompt: input
    });

    // API'den gelen yanıtı (string ise) parse ediyoruz
    let rawAnswer = res.data.answer;
    let finalContent = "";
    let extractedMovies = [];

    try {
      // Yanıt bir JSON string ise parse et
      const parsed = typeof rawAnswer === 'string' ? JSON.parse(rawAnswer) : rawAnswer;
      
      if (parsed.type === "movie_list") {
        finalContent = parsed.text; // "IMDb 7 ve üzeri..." metni
        extractedMovies = parsed.movies; // Film listesi dizisi
      } else {
        finalContent = rawAnswer;
      }
    } catch (parseError) {
      // Eğer JSON değilse düz metin olarak kabul et
      finalContent = rawAnswer;
    }

    const botMsg = { 
      role: 'assistant', 
      content: finalContent, 
      movies: extractedMovies 
    };

    setMessages((prev: any) => [...prev, botMsg]);
    fetchSessions();
  } catch (e) { 
    console.log("Chat hatası:", e); 
    setMessages((prev: any) => [...prev, { role: 'assistant', content: "Bir hata oluştu." }]);
  } finally { 
    setLoading(false); 
  }
};

  return (
    <SafeAreaView style={styles.container}>
      {/* KRİTİK DEĞİŞİKLİK: 
        Android'de 'padding' bazen 'height'dan daha iyi çalışır. 
        Offset değerine header yüksekliğini ekliyoruz.
      */}
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'padding'}
        style={{ flex: 1 }}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : headerHeight + 60} 
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.openDrawer()}>
            <Menu color="#fff" size={24} />
          </TouchableOpacity>
          <View style={styles.headerTitleContainer}>
            <Film color="#E50914" size={20} />
            <Text style={styles.headerText}>Movie AI</Text>
          </View>
        </View>

        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(_, index) => index.toString()}
          contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          // Klavye açıldığında listenin otomatik kayması için:
          maintainVisibleContentPosition={{ minIndexForVisible: 0 }}
          keyboardDismissMode="on-drag"
          keyboardShouldPersistTaps="handled"
// Chat.tsx içinde renderItem kısmını şu şekilde güncelle:
          renderItem={({ item }) => (
            <View style={[styles.msgBox, item.role === 'user' ? styles.userMsg : styles.botMsg]}>
              <Text style={styles.text}>{item.content}</Text>
              {item.movies && item.movies.map((movie: any, i: number) => (
                <MovieCard key={i} movie={movie} userId={userId} /> // userId'yi burada geçiyoruz
              ))}
            </View>
          )}
        />

        <View style={styles.inputArea}>
          <TextInput
            style={styles.input}
            value={input}
            onChangeText={setInput}
            placeholder="Film sor..."
            placeholderTextColor="#666"
            onSubmitEditing={handleSend} // Klavyedeki "Bitti/Gönder" butonu için
          />
          <TouchableOpacity onPress={handleSend} disabled={loading} style={styles.sendButton}>
            {loading ? <ActivityIndicator color="#E50914" /> : <Send color="#E50914" size={24} />}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  header: { 
    flexDirection: 'row', 
    padding: 15, 
    alignItems: 'center', 
    backgroundColor: '#121212',
    paddingTop: Platform.OS === 'android' ? 10 : 0 // Android StatusBar çakışması için
  },
  headerTitleContainer: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginRight: 24 },
  headerText: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginLeft: 8 },
  listContent: { padding: 15, paddingBottom: 20 },
  msgBox: { padding: 12, borderRadius: 15, marginBottom: 10, maxWidth: '85%' },
  userMsg: { alignSelf: 'flex-end', backgroundColor: '#E50914' },
  botMsg: { alignSelf: 'flex-start', backgroundColor: '#222' },
  text: { color: '#fff', fontSize: 15 },
  inputArea: { 
    flexDirection: 'row', 
    padding: 10, 
    paddingBottom: Platform.OS === 'ios' ? 25 : 15, // Alttaki navigasyon barı payı
    alignItems: 'center', 
    backgroundColor: '#121212',
    borderTopWidth: 1,
    borderTopColor: '#333'
  },
  input: { 
    flex: 1, 
    color: '#fff', 
    backgroundColor: '#222', 
    borderRadius: 25, 
    paddingHorizontal: 18, 
    height: 48, 
    marginRight: 10 
  },
  sendButton: { width: 48, height: 48, justifyContent: 'center', alignItems: 'center' }
});

export default Chat;