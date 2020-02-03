#pragma once

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
class SharedMemory
{
	public:

		SharedMemory();
		SharedMemory(const wstring& strName, DWORD dwSize, bool bSyncObjects = true, bool bCreate = true);

		~SharedMemory();

		void Create(const wstring& strName, DWORD dwSize = 1, bool bSyncObjects = true);
		void Open(const wstring& strName, bool bSync = true);

		inline void Lock();
		inline void Release();
		inline void SetEvent();

		inline T* Get() const;
		inline HANDLE GetEvent() const;

		inline T& operator[](size_t index) const;
		inline T* operator->() const;
		inline T& operator*() const;
		inline SharedMemory& operator=(const T& val);

	private:

		void CreateSyncObjects(const wstring& strName);

	private:

		wstring				m_strName;
		DWORD				m_dwSize;

		shared_ptr<void>	m_hSharedMem;
		shared_ptr<T>		m_pSharedMem;

		shared_ptr<void>	m_hSharedMutex;
		shared_ptr<void>	m_hSharedEvent;
};

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

class SharedMemoryLock
{
	public:

		template <typename T> explicit SharedMemoryLock(SharedMemory<T>& sharedMem)
		: m_lock((sharedMem.Lock(), &sharedMem), mem_fn(SharedMemory<T>::Release))
		{
		}

	private:

		shared_ptr<void>	m_lock;
};

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
SharedMemory<T>::SharedMemory()
: m_strName(L"")
, m_dwSize(0)
, m_hSharedMem()
, m_pSharedMem()
, m_hSharedMutex()
, m_hSharedEvent()
{
}


template<typename T>
SharedMemory<T>::SharedMemory(const wstring& strName, DWORD dwSize, bool bSyncObjects, bool bCreate)
: m_strName(strName)
, m_dwSize(dwSize)
{
	if (bCreate)
	{
		Create(strName, dwSize, bSyncObjects);
	}
	else
	{
		Open(strName, bSyncObjects);
	}
}


template<typename T>
SharedMemory<T>::~SharedMemory()
{
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
void SharedMemory<T>::Create(const wstring& strName, DWORD dwSize, bool bSyncObjects)
{
	m_strName	= strName;
	m_dwSize	= dwSize;

	m_hSharedMem = shared_ptr<void>(::CreateFileMapping(
										INVALID_HANDLE_VALUE, 
										NULL, 
										PAGE_READWRITE, 
										0, 
										m_dwSize * sizeof(T), 
										m_strName.c_str()),
									::CloseHandle);

	// TODO: error handling
	//if (m_hSharedMem.get() == NULL) return false;

	m_pSharedMem = shared_ptr<T>(static_cast<T*>(::MapViewOfFile(
													m_hSharedMem.get(), 
													FILE_MAP_ALL_ACCESS, 
													0, 
													0, 
													0)),
												::UnmapViewOfFile);

	if (bSyncObjects) CreateSyncObjects(strName);

	//if (m_pSharedMem.get() == NULL) return false;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
void SharedMemory<T>::Open(const wstring& strName, bool bSyncObjects)
{
	m_strName	= strName;

	m_hSharedMem = shared_ptr<void>(::OpenFileMapping(
										FILE_MAP_ALL_ACCESS, 
										FALSE, 
										m_strName.c_str()),
									::CloseHandle);

	// TODO: error handling
	//if (m_hSharedMem.get() == NULL) return false;

	m_pSharedMem = shared_ptr<T>(static_cast<T*>(::MapViewOfFile(
													m_hSharedMem.get(), 
													FILE_MAP_ALL_ACCESS, 
													0, 
													0, 
													0)),
												::UnmapViewOfFile);

	if (bSyncObjects) CreateSyncObjects(strName);

	//if (m_pSharedMem.get() == NULL) return false;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
void SharedMemory<T>::Lock()
{
	if (m_hSharedMutex.get() == NULL) return;
	::WaitForSingleObject(m_hSharedMutex.get(), INFINITE);
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
void SharedMemory<T>::Release()
{
	if (m_hSharedMutex.get() == NULL) return;
	::ReleaseMutex(m_hSharedMutex.get());
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
void SharedMemory<T>::SetEvent()
{
	if (m_hSharedEvent.get() == NULL) return;
	::SetEvent(m_hSharedEvent.get());
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
T* SharedMemory<T>::Get() const
{
	return m_pSharedMem.get();
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
HANDLE SharedMemory<T>::GetEvent() const
{
	return m_hSharedEvent.get();
}

//////////////////////////////////////////////////////////////////////////////


template<typename T>
T& SharedMemory<T>::operator[](size_t index) const
{
	return *(m_pSharedMem.get() + index);
}

//////////////////////////////////////////////////////////////////////////////

template<typename T>
T* SharedMemory<T>::operator->() const
{
	return m_pSharedMem.get();
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
T& SharedMemory<T>::operator*() const
{
	return *m_pSharedMem;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
SharedMemory<T>& SharedMemory<T>::operator=(const T& val)
{
	*m_pSharedMem = val;
	return *this;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template<typename T>
void SharedMemory<T>::CreateSyncObjects(const wstring& strName)
{
	m_hSharedMutex = shared_ptr<void>(
						::CreateMutex(NULL, FALSE, (strName + wstring(L"_mutex")).c_str()),
						::CloseHandle);

	m_hSharedEvent = shared_ptr<void>(
						::CreateEvent(NULL, FALSE, FALSE, (strName + wstring(L"_event")).c_str()),
						::CloseHandle);
}

//////////////////////////////////////////////////////////////////////////////