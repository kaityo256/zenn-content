# frozen_string_literal: true

require "json"

# zenn.json を読み込んで Ruby の Hash を返す
def load_zenn_json(path = "zenn.json")
  unless File.file?(path)
    raise ArgumentError, "File not found: #{path}"
  end

  raw = File.read(path, encoding: "UTF-8")
  data = JSON.parse(raw) # => Hash or Array

  unless data.is_a?(Hash)
    raise TypeError, "Expected top-level JSON object (Hash), got: #{data.class}"
  end

  data
rescue JSON::ParserError => e
  raise JSON::ParserError, "Invalid JSON in #{path}: #{e.message}"
end

# Hash としてデータを受け取って処理する（ここを好きに実装）
def handle_zenn(data)
  unless data.is_a?(Hash)
    raise TypeError, "handle_zenn expects Hash, got: #{data.class}"
  end

  # ---- サンプル処理（必要に応じて置き換えてください） ----
  puts "Top-level keys: #{data.keys.sort.join(', ')}"
  puts "Top-level entries: #{data.size}"

  # よくあるキー例に対する安全なアクセス例（存在しなければ nil）
  title = data["title"]
  puts "title: #{title.inspect}" if title
end

json = load_zenn_json("zenn.json")

json['articles'].each do |a|
  puts a['title']
  puts a['slug']
  puts a['published_at']
end