import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { createDrawerNavigator, DrawerContentScrollView } from '@react-navigation/drawer';
import { Plus, LogOut, MessageSquare, Trash2, User as UserIcon } from 'lucide-react-native';
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

// Bileşenlerini import et
import AuthScreen from '../components/AuthScreen';
import Chat from '../components/Chat';

const Drawer = createDrawerNavigator();
const API_BASE_URL = 'http://localhost:8000';

const CustomDrawerContent = (props: any) => {
  const { userId, username, currentSessionId, setSessionId, sessions, fetchSessions, setUser } = props;

  const handleNewChat = () => {
    const newId = uuidv4();
    setSessionId(newId);
    props.navigation.closeDrawer();
  };

  const handleDeleteSession = async (sId: string) => {
    Alert.alert("Sohbeti Sil", "Bu sohbet geçmişi kalıcı olarak silinecek.", [
      { text: "İptal", style: "cancel" },
      { text: "Sil", style: 'destructive', onPress: async () => {
        try {
          await axios.delete(`${API_BASE_URL}/chat/${userId}/${sId}`);
          fetchSessions();
          if (currentSessionId === sId) handleNewChat();
        } catch (e) { console.error(e); }
      }}
    ]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: '#121212' }}>
      <DrawerContentScrollView {...props}>
        <View style={styles.sidebarHeader}>
          <UserIcon color="#E50914" size={24} />
          <Text style={styles.usernameText}>{username}</Text>
        </View>

        <View style={styles.sidebarActions}>
          <TouchableOpacity style={styles.newChatBtn} onPress={handleNewChat}>
            <Plus color="#fff" size={20} />
            <Text style={styles.btnText}>Yeni Sohbet</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.logoutBtn} onPress={() => setUser(null)}>
            <LogOut color="#fff" size={20} />
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>Geçmiş Sohbetler</Text>
        {sessions.map((s: any) => (
          <View key={s.session_id} style={[styles.sessionItem, currentSessionId === s.session_id && styles.activeSession]}>
            <TouchableOpacity 
              style={{ flex: 1, flexDirection: 'row', alignItems: 'center' }}
              onPress={() => { setSessionId(s.session_id); props.navigation.closeDrawer(); }}
            >
              <MessageSquare color={currentSessionId === s.session_id ? "#E50914" : "#888"} size={18} />
              <Text numberOfLines={1} style={[styles.sessionText, currentSessionId === s.session_id && styles.activeText]}>
                {s.title || "İsimsiz Sohbet"}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => handleDeleteSession(s.session_id)}>
              <Trash2 color="#555" size={18} />
            </TouchableOpacity>
          </View>
        ))}
      </DrawerContentScrollView>
    </View>
  );
};

export default function App() {
  const [user, setUser] = useState<{ id: number; name: string } | null>(null);
  const [sessionId, setSessionId] = useState(uuidv4());
  const [sessions, setSessions] = useState([]);
  const [messages, setMessages] = useState([]); // Chat state'ini burada yönetmek st.session_state mantığına daha yakın

  const handleLoginSuccess = (id: number, name: string) => {
    setUser({ id, name });
  };

  const fetchSessions = async () => {
    if (!user) return;
    try {
      const res = await axios.get(`${API_BASE_URL}/sessions/${user.id}`);
      setSessions(res.data.sessions || []);
    } catch (e) { console.error("Session listesi alınamadı", e); }
  };

  useEffect(() => {
    if (user) fetchSessions();
  }, [user, sessionId]);

  if (!user) {
    return <AuthScreen onLoginSuccess={handleLoginSuccess} />;
  }

  // ÇÖZÜM: NavigationContainer kaldırıldı, direkt Drawer.Navigator döndürülüyor.
  return (
      <Drawer.Navigator
        drawerContent={(props) => (
          <CustomDrawerContent 
            {...props} 
            userId={user.id} 
            username={user.name}
            currentSessionId={sessionId}
            setSessionId={setSessionId}
            sessions={sessions}
            fetchSessions={fetchSessions}
            setUser={setUser}
          />
        )}
        screenOptions={{ 
          headerShown: false, 
          drawerStyle: { width: '80%' },
          swipeEnabled: true 
        }}
      >
        <Drawer.Screen name="ChatMain">
          {(props) => (
            <Chat 
              {...props} 
              userId={user.id} 
              username={user.name} 
              sessionId={sessionId} 
              messages={messages}
              setMessages={setMessages}
              fetchSessions={fetchSessions}
            />
          )}
        </Drawer.Screen>
      </Drawer.Navigator>
  );
}

const styles = StyleSheet.create({
  sidebarHeader: { padding: 20, flexDirection: 'row', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#333' },
  usernameText: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginLeft: 10 },
  sidebarActions: { flexDirection: 'row', padding: 15, justifyContent: 'space-between' },
  newChatBtn: { flex: 1, backgroundColor: '#E50914', flexDirection: 'row', padding: 12, borderRadius: 8, alignItems: 'center', justifyContent: 'center', marginRight: 10 },
  logoutBtn: { backgroundColor: '#333', padding: 12, borderRadius: 8, justifyContent: 'center' },
  btnText: { color: '#fff', marginLeft: 8, fontWeight: '600' },
  sectionTitle: { color: '#666', fontSize: 12, marginLeft: 20, marginBottom: 10, textTransform: 'uppercase', marginTop: 10 },
  sessionItem: { flexDirection: 'row', padding: 12, marginHorizontal: 10, borderRadius: 8, marginBottom: 4 },
  activeSession: { backgroundColor: '#222' },
  sessionText: { color: '#aaa', marginLeft: 10, fontSize: 14 },
  activeText: { color: '#fff', fontWeight: 'bold' }
});